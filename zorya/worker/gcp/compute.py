"""Interactions with compute engine."""
import backoff
from googleapiclient import discovery
from googleapiclient.errors import HttpError

from zorya.worker.logging import Logger
from zorya.util import utils


class Compute(object):
    """Compute engine actions."""

    def __init__(self, project, logger=None):
        self.compute = discovery.build("compute", "v1", cache_discovery=False)
        self.project = project
        self.logger = logger or Logger()

    def change_status(self, action, tagkey, tagvalue):
        """
        Stop/start instance based on tags
        Args:
            action: 0 stop 1 start
            tagkey: tag key
            tagvalue: tag value
        """
        tag_filter = "labels." + tagkey + "=" + tagvalue
        instances = self.list_instances(tag_filter)

        if not instances:
            self.logger("skipping state change for GCE instances")
            return

        self.logger(
            f"running state change for {len(instances)} compute instances"
        )
        for instance in instances:
            if int(action) == 1:
                self.logger("Starting compute instance", instance=instance)
                self.start_instance(instance["zone"], instance["name"])
            else:
                self.logger("Stopping compute instance", instance=instance)
                self.stop_instance(instance["zone"], instance["name"])
        return

    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code
    )
    def stop_instance(self, zone, instance):
        """
        Stop an instance.
        Args:
            zone: zone
            instance: instance name
        """
        # TODO add requestId
        return (
            self.compute.instances()
            .stop(project=self.project, zone=zone, instance=instance)
            .execute()
        )

    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code
    )
    def start_instance(self, zone, instance):
        """
        Start an instance.
        Args:
            zone: zone
            instance: instance name
        """
        # TODO add requestId
        return (
            self.compute.instances()
            .start(project=self.project, zone=zone, instance=instance)
            .execute()
        )

    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code
    )
    def list_instances(self, tags_filter=None):
        """
        List all instances in zone with the requested tags
        Args:
            zone: zone
            tags_filter: tags
        """
        result = (
            self.compute.instances()
            .aggregatedList(project=self.project, filter=tags_filter)
            .execute()
        )
        return result.get("items", [])
