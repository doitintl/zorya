"""Interactions with compute engine."""
import backoff
import google.auth
from requests.exceptions import HTTPError

from zorya.logging import Logger
from zorya.resources.utils import fatal_code
from zorya.model.state_change import StateChange


class CloudSql(object):
    def __init__(self, state_change: StateChange, logger: Logger = None):
        self.state_change = state_change
        self.logger = logger or Logger()

        credentials, _ = google.auth.default()
        self.authed_session = google.auth.AuthorizedSession(credentials)
        self.tag_filter = (
            "settings.userLabels."
            f"{state_change.tagkey}={state_change.tagvalue}"
        )
        self.instances = self.list_instances(self.tag_filter)

    def change_status(self):
        self.logger(
            f"running state change for {len(self.instances)} CloudSQL instances"
        )
        for instance in self.instances:
            logger = self.logger.refine(instance=instance)
            if int(self.change_status.action) == 1:
                logger("Starting CloudSQL instance", instance=instance)
                self.start_instance(instance["name"])
            else:
                logger("Stopping CloudSQL instance", instance=instance)
                self.stop_instance(instance["name"])

    @backoff.on_exception(
        backoff.expo, HTTPError, max_tries=8, giveup=fatal_code
    )
    def stop_instance(self, instance):
        prev_instance_data = self.authed_session.get(
            "https://sqladmin.googleapis.com/sql/v1beta4/projects"
            f"/{self.change_status.project}/instances/{instance}",
        )

        patch_body = {
            "settings": {
                "settingsVersion": prev_instance_data["settings"][
                    "settingsVersion"
                ],
                "activationPolicy": "NEVER",
            }
        }

        res = self.authed_session.patch(
            "https://sqladmin.googleapis.com/sql/v1beta4/projects"
            f"/{self.change_status.project}/instances/{instance}",
            data=patch_body,
        )
        res.raise_for_status()
        return res.json()

    @backoff.on_exception(
        backoff.expo, HTTPError, max_tries=8, giveup=fatal_code
    )
    def start_instance(self, instance):
        prev_instance_data = self.authed_session.get(
            "https://sqladmin.googleapis.com/sql/v1beta4/projects"
            f"/{self.change_status.project}/instances/{instance}",
        )

        patch_body = {
            "settings": {
                "settingsVersion": prev_instance_data["settings"][
                    "settingsVersion"
                ],
                "activationPolicy": "ALWAYS",
            }
        }

        res = self.authed_session.patch(
            "https://sqladmin.googleapis.com/sql/v1beta4/projects"
            f"/{self.change_status.project}/instances/{instance}",
            body=patch_body,
        )
        res.raise_for_status()
        return res.json()

    @backoff.on_exception(
        backoff.expo, HTTPError, max_tries=8, giveup=fatal_code
    )
    def list_instances(self, tags_filter=None):
        res = self.authed_session.get(
            "https://sqladmin.googleapis.com/sql/v1beta4/projects"
            f"/{self.state_change.project}/instances?filter={tags_filter}",
            project=self.change_status.project,
        )

        res.raise_for_status()
        return res.json().get("items", [])
