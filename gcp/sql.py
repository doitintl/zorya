"""Interactions with compute engine."""

import logging

import backoff
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from util import utils

CREDENTIALS = None


class Sql(object):
    """Compute engine actions."""

    def __init__(self, project):
        self.sql = discovery.build(
            "sqladmin",
            "v1beta4",
            credentials=CREDENTIALS,
            cache_discovery=False,
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
        tag_filter = "settings.userLabels." + tagkey + "=" + tagvalue
        logging.debug("Filter %s", filter)
        try:
            instances = self.list_instances(tag_filter)
            for instance in instances:
                if int(to_status) == 1:
                    logging.info(
                        "Starting SQL %s in project %s tagkey %s tagvalue %s",
                        instance["name"],
                        self.project,
                        tagkey,
                        tagvalue,
                    )
                    self.start_instance(instance["name"])
                else:
                    logging.info(
                        "Stopping SQL %s in project %s tagkey %s tagvalue %s",
                        instance["name"],
                        self.project,
                        tagkey,
                        tagvalue,
                    )
                    self.stop_instance(instance["name"])
        except HttpError as http_error:
            logging.error(http_error)
            return "Error", 500
        return "ok", 200

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

        Returns:

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
