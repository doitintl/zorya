"""Interactions with compute engine."""
import logging

import backoff
from google.auth import app_engine
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from util import gcp, utils

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

CREDENTIALS = app_engine.Credentials(scopes=SCOPES)


class Instancegroup(object):
    """Compute engine actions."""


    def __init__(self, project):
        self.compute = discovery.build(
            'compute', 'v1', credentials=CREDENTIALS)
        self.project = project


    def change_status(self, to_status):
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
                instanceGroupManagers = self.list_instanceGroupManagers(zone, tag_filter)
                for instanceGroupManager in instanceGroupManagers:
                    if int(to_status) == 1:
                        logging.info("Starting %s in project %s", instanceGroupManager['name'], self.project, tagkey, tagvalue)
                        self.start_instanceGroupManager(zone, instanceGroupManager['name'])
                    else:
                        logging.info("Stopping %s in project %s", instanceGroupManager['name'], self.project, tagkey, tagvalue)
                        self.stop_instanceGroupManager(zone, instanceGroupManager['name'])
            except HttpError as http_error:
                logging.error(http_error)
                return 'Error', 500
        return 'ok', 200


    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def stop_instanceGroupManager(self, zone, instanceGroupManager):
        """
        Stop an instance.
        Args:
            zone: zone
            instance: instance name

        Returns:

        """
        size = 0
        logging.info("instance_group_manager is %s in project %s is set to %", instanceGroupManager['name'], self.project, size)
        return self.instanceGroupManagers().resize(project=project, zone=zone, instanceGroupManager=instance_group_manager, size=size).execute()
              

    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def start_instanceGroupManager(self, zone, instanceGroupManager):
        """
        Start an instance.
        Args:
            zone: zone
            instance: instance name

        Returns:

        """
        size = 1
        logging.info("instance_group_manager is %s in project %s is set to %", instanceGroupManager['name'], self.project, size)
        return self.instanceGroupManagers().resize(project=project, zone=zone, instanceGroupManager=instance_group_manager, size=size).execute()      


    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def list_instanceGroupManagers(self, zone, tags_filter=None):
        """
        List all instances group managers in zone
        Args:
            zone: zone
            tags_filter: tags

        Returns:

        """
        result = self.instanceGroupManagers().list(project=project, zone=zone, filter=tags_filter).execute()                      
        if 'items' in result:
            return result['items']
        else:
            return []
