"""Interactions with compute engine."""
import backoff
import google.auth
from requests.exceptions import HTTPError

from zorya.logging import Logger
from zorya.resources.utils import fatal_code
from zorya.model.state_change import StateChange


class GoogleComputEngine(object):
    def __init__(self, state_change: StateChange, logger: Logger = None):
        self.state_change = state_change
        self.logger = logger or Logger()

        credentials, _ = google.auth.default()
        self.authed_session = google.auth.AuthorizedSession(credentials)
        self.tag_filter = (
            f"labels.{state_change.tagkey}={state_change.tagvalue}"
        )
        self.instances = self.list_instances(self.tag_filter)

    def change_status(self):
        self.logger(
            f"running state change for {len(self.instances)} compute instances"
        )
        for instance in self.instances:
            if int(self.state_change.action) == 1:
                self.logger("Starting compute instance", instance=instance)
                self.start_instance(instance["zone"], instance["name"])
            else:
                self.logger("Stopping compute instance", instance=instance)
                self.stop_instance(instance["zone"], instance["name"])
        return

    @backoff.on_exception(
        backoff.expo,
        HTTPError,
        max_tries=8,
        giveup=fatal_code,
    )
    def stop_instance(self, zone, instance_name):
        return self.authed_session(
            "https://compute.googleapis.com/compute/v1/projects"
            f"/{self.state_change.project}/zones/{zone}/instances/{instance_name}/stop"
        )

    @backoff.on_exception(
        backoff.expo,
        HTTPError,
        max_tries=8,
        giveup=fatal_code,
    )
    def start_instance(self, zone, instance_name):
        return self.authed_session(
            "https://compute.googleapis.com/compute/v1/projects"
            f"/{self.state_change.project}/zones/{zone}/instances/{instance_name}/start"
        )

    @backoff.on_exception(
        backoff.expo,
        HTTPError,
        max_tries=8,
        giveup=fatal_code,
    )
    def list_instances(self):
        result = self.authed_session.get(
            f"https://compute.googleapis.com/compute/v1/projects"
            f"/{self.change_status.project}/aggregated/instances"
            f"?filter={self.tag_filter}"
        )
        return result.get("items", [])
