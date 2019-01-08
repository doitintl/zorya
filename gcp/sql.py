"""Interactions with compute engine."""

import logging

import backoff
from google.auth import app_engine
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from util import utils

SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']

CREDENTIALS = app_engine.Credentials(scopes=SCOPES)


class Sql(object):
    """Compute engine actions."""


    def __init__(self, project):
        self.sql = discovery.build(
            'sqladmin', 'v1beta4', credentials=CREDENTIALS)
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
        tag_filter = "userLabels." + tagkey + "=" + tagvalue
        logging.debug("Filter %s", filter)
        try:
            instances = self.list_instances(tag_filter)
            for instance in instances:
                if int(to_status) == 1:
                    logging.info(
                        "Starting SQL %s in project %s tagkey %s tagvalue %s",
                        instance['name'], self.project, tagkey, tagvalue)
                    self.start_instance(instance['name'])
                else:
                    logging.info(
                        "Stopping SQL %s in project %s tagkey %s tagvalue %s",
                        instance['name'], self.project, tagkey, tagvalue)
                    self.stop_instance(instance['name'])
        except HttpError as http_error:
            logging.error(http_error)
            return 'Error', 500
        return 'ok', 200


    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
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
            database_instance_body = self.sql.instances().get(
                project=self.project, instance=instance).execute()
            database_instance_body['settings']['activationPolicy'] = "NEVER"
            res = self.sql.instances().patch(instance=instance,
                                             project=self.project,
                                             body=database_instance_body).execute()
        except Exception as e:
            logging.error(e)
        return res


    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def start_instance(self, instance):
        """
        Start an instance.
        Args:
            zone: zone
            instance: instance name

        Returns:

        """
        try:
            database_instance_body = self.sql.instances().get(
                project=self.project, instance=instance).execute()
            database_instance_body['settings']['activationPolicy'] = "ALWAYS"
            res = self.sql.instances().patch(instance=instance,
                                             project=self.project,
                                             body=database_instance_body).execute()
        except Exception as e:
            logging.error(e)
        return res


    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def list_instances(self, tags_filter=None):
        """
        List all instances in  with the requested tags
        Args:
            zone: zone
            tags_filter: tags

        Returns:

        """
        result = self.sql.instances().list(
            project=self.project, filter=tags_filter).execute()
        if 'items' in result:
            return result['items']
        else:
            return []
