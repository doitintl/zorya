"""Interactions with compute engine."""
import logging

import backoff
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from util import utils

CREDENTIALS = None


class Gae(object):
    """App Engine actions."""

    def __init__(self, project):
        self.app = discovery.build(
            'appengine', 'v1', credentials=CREDENTIALS, cache_discovery=False
        )
        self.project = project

    def change_status(self, to_status, service_id, version_id):
        """
        Stop/start version based on tags
        Args:
            to_status: 0 stop 1 start
            service_id: The App Engine service id
            version_id: The App Engine version id

        Returns:

        """

        try:
            if int(to_status) == 1:
                logging.info(
                    "Starting App Engine service: %s version: %s on project: %s",
                    service_id,
                    version_id,
                    self.project
                )
                self.stop_version(service_id, version_id)

            else:
                logging.info(
                    "Stopping App Engine service: %s version: %s on project: %s",
                    service_id,
                    version_id,
                    self.project
                )
                self.start_version(service_id, version_id)

        except HttpError as http_error:
            logging.error(http_error)
            return "Error", 500
        return "ok", 200

    @backoff.on_exception(backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def stop_version(self, service_id, version_id):
        """
        Stop an instance.
        Args:
            service_id: The App Engine service id
            version_id: The App Engine version id

        Returns:

        """
        # TODO add requestId
        return (
            self.app.apps().services().versions().patch(servicesId=service_id, appsId=self.project,
                                                        versionsId=version_id, updateMask='servingStatus',
                                                        body={"servingStatus": "STOPPED"}).execute()
        )

    @backoff.on_exception(backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def start_version(self, service_id, version_id):
        """
        Start an instance.
        Args:
            service_id: The App Engine service id
            version_id: The App Engine version id

        Returns:

        """
        # TODO add requestId
        return (
            self.app.apps().services().versions().patch(servicesId=service_id, appsId=self.project,
                                                        versionsId=version_id, updateMask='servingStatus',
                                                        body={"servingStatus": "SERVING"}).execute()
        )
