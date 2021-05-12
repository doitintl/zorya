"""Interactions with compute engine."""
import logging

import backoff
from googleapiclient import discovery
from googleapiclient.errors import HttpError

from zorya.worker.logging import Logger
from zorya.util import utils


class Sql(object):
    """Compute engine actions."""

    def __init__(self, project, logger=None):
        self.sql = discovery.build(
            "sqladmin", "v1beta4", cache_discovery=False
        )
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
        tag_filter = "settings.userLabels." + tagkey + "=" + tagvalue

        instances = self.list_instances(tag_filter)
        if not instances:
            self.logger("skipping state change for CloudSQL instances")
            return

        self.logger(
            f"running state change for {len(instances)} CloudSQL instances"
        )
        for instance in instances:
            logger = self.logger.refine(instance=instance)
            if int(action) == 1:
                logger("Starting CloudSQL instance", instance=instance)
                self.start_instance(instance["name"])
            else:
                logger("Stopping CloudSQL instance", instance=instance)
                self.stop_instance(instance["name"])

        return

    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code
    )
    def stop_instance(self, instance):
        """
        Stop an instance.
        Args:
            zone: zone
            instance: instance name

        Returns:

        """
        # TODO add requestId
        try:
            prev_instance_data = (
                self.sql.instances()
                .get(project=self.project, instance=instance)
                .execute()
            )

            patch_body = {
                "settings": {
                    "settingsVersion": prev_instance_data["settings"][
                        "settingsVersion"
                    ],
                    "activationPolicy": "NEVER",
                }
            }

            res = (
                self.sql.instances()
                .patch(
                    project=self.project,
                    instance=instance,
                    body=patch_body,
                )
                .execute()
            )
            return res

        except Exception as e:
            logging.error(e)
        return

    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code
    )
    def start_instance(self, instance):
        """
        Start an instance.
        Args:
            zone: zone
            instance: instance name
        """
        try:
            prev_instance_data = (
                self.sql.instances()
                .get(project=self.project, instance=instance)
                .execute()
            )

            patch_body = {
                "settings": {
                    "settingsVersion": prev_instance_data["settings"][
                        "settingsVersion"
                    ],
                    "activationPolicy": "ALWAYS",
                }
            }

            res = (
                self.sql.instances()
                .patch(
                    project=self.project,
                    instance=instance,
                    body=patch_body,
                )
                .execute()
            )
            return res
        except Exception as e:
            logging.error(e)
        return

    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code
    )
    def list_instances(self, tags_filter=None):
        """
        List all instances in  with the requested tags
        Args:
            zone: zone
            tags_filter: tags

        Returns:

        """
        result = (
            self.sql.instances()
            .list(project=self.project, filter=tags_filter)
            .execute()
        )
        if "items" in result:
            return result["items"]
        else:
            return []
