"""Interactions with compute engine."""
import logging

import backoff
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from util import gcp, utils

CREDENTIALS = None


class Compute(object):
    """Compute engine actions."""

    def __init__(self, project):
        self.compute = discovery.build(
            "compute", "v1", credentials=CREDENTIALS, cache_discovery=False
        )
        self.project = project

    def change_status(self, to_status, tagkey, tagvalue):
        """
        Stop/start instance based on tags
        Args:
            to_status: 0 stop 1 start
            tagkey: tag key
            tagvalue: tag value

        Returns:

        """
        tag_filter = "labels." + tagkey + "=" + tagvalue
        logging.debug("Filter %s", filter)
        for zone in gcp.get_zones():
            try:
                instances = self.list_instances(zone, tag_filter)
                for instance in instances:
                    if int(to_status) == 1:
                        logging.info(
                            "Starting %s in project %s tagkey %s tagvalue %s",
                            instance["name"],
                            self.project,
                            tagkey,
                            tagvalue,
                        )
                        self.start_instance(zone, instance["name"])
                    else:
                        logging.info(
                            "Stopping %s in project %s tagkey %s tagvalue %s",
                            instance["name"],
                            self.project,
                            tagkey,
                            tagvalue,
                        )
                        self.stop_instance(zone, instance["name"])
            except HttpError as http_error:
                logging.error(http_error)
                return "Error", 500
        return "ok", 200

    @backoff.on_exception(backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def stop_instance(self, zone, instance):
        """
        Stop an instance.
        Args:
            zone: zone
            instance: instance name

        Returns:

        """
        # TODO add requestId
        return (
            self.compute.instances()
            .stop(project=self.project, zone=zone, instance=instance)
            .execute()
        )

    @backoff.on_exception(backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def start_instance(self, zone, instance):
        """
        Start an instance.
        Args:
            zone: zone
            instance: instance name

        Returns:

        """
        # TODO add requestId
        return (
            self.compute.instances()
            .start(project=self.project, zone=zone, instance=instance)
            .execute()
        )

    @backoff.on_exception(backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def list_instances(self, zone, tags_filter=None):
        """
        List all instances in zone with the requested tags
        Args:
            zone: zone
            tags_filter: tags

        Returns:

        """
        result = (
            self.compute.instances()
            .list(project=self.project, zone=zone, filter=tags_filter)
            .execute()
        )
        if "items" in result:
            return result["items"]
        else:
            return []
