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
    """Instance Group actions."""


    def __init__(self, project):
        self.compute = discovery.build(
            'compute', 'v1', credentials=CREDENTIALS)
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
                if int(to_status) == 1:
                    logging.info("Starting %s in project %s tagkey %s tagvalue %s", self.project, tagkey, tagvalue)
                    self.expand_instances_group(zone)
                else:
                    logging.info("Stopping %s in project %s tagkey %s tagvalue %s", self.project, tagkey, tagvalue)
                    self.reduce_instances_group(zone)
            except HttpError as http_error:
                logging.error(http_error)
                return 'Error', 500
        return 'ok', 200
 
    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    # Arret
    # Recherche de tous les groupes d'instance du projet pour la zone.
    def reduce_instances_group(zone):
        request = service.instanceGroupManagers().list(project=project, zone=zone)
        while request is not None:
            response = request.execute()

            for instance_group_manager in response['items']:
                # TODO: Change code below to process each `instance_group_manager` resource:
                #pprint(instance_group_manager)
                name = instance_group_manager['baseInstanceName']
                name = "%s-grp"%(name)
                print(name)
                # The number of running instances that the managed instance group should maintain at any given time.
                # The group automatically adds or removes instances to maintain the number of instances specified by
                # this parameter.
                size = 0  # TODO: Update placeholder value.

                request = service.instanceGroupManagers().resize(project=project, zone=zone, instanceGroupManager=name, size=size)
                response = request.execute()

                # TODO: Change code below to process the `response` dict:
                #pprint(response)
            request = service.instanceGroupManagers().list_next(previous_request=request, previous_response=response)
        #pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        #print(pubsub_message)
    
    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    # Start
    # Recherche de tous les groupes d'instance du projet pour la zone.
    def expand_instances_group(zone):
        request = service.instanceGroupManagers().list(project=project, zone=zone)
        while request is not None:
            response = request.execute()

            for instance_group_manager in response['items']:
                # TODO: Change code below to process each `instance_group_manager` resource:
                #pprint(instance_group_manager)
                name = instance_group_manager['baseInstanceName']
                name = "%s-grp"%(name)
                print(name)
                # The number of running instances that the managed instance group should maintain at any given time.
                # The group automatically adds or removes instances to maintain the number of instances specified by
                # this parameter.
                size = 1  # TODO: Update placeholder value.

                request = service.instanceGroupManagers().resize(project=project, zone=zone, instanceGroupManager=name, size=size)
                response = request.execute()

                # TODO: Change code below to process the `response` dict:
                #pprint(response)
            request = service.instanceGroupManagers().list_next(previous_request=request, previous_response=response)
        #pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        #print(pubsub_message)
