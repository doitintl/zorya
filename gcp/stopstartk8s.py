"""Interactions with compute engine."""
import logging

import backoff
from google.auth import app_engine
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from util import gcp, utils

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

CREDENTIALS = app_engine.Credentials(scopes=SCOPES)

class Stopstartk8s(object):
    """Compute engine actions."""

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
                    logging.debug("Augment k8s cluster pour project %s dans la zone %s", self.project, zone)
                    #self.start_k8s(project, zone)
                else:
                    logging.debug("Reduce k8s cluster pour project %s dans la zone %s", self.project, zone)
                    #self.stop_k8s(project, zone)
            except HttpError as http_error:
                logging.error(http_error)
                return 'Error', 500
        return 'ok', 200
     
    # Arret
    # Recherche de tous les groupes d'instance du projet pour la zone.
    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def stop_k8s(self, project, zone):
        request = self.instanceGroupManagers().list(project=project, zone=zone)
        while request is not None:
            response = request.execute()
            for instance_group_manager in response['items']:
                name = instance_group_manager['baseInstanceName']
                name = "%s-grp"%(name)
                logging.debug("Reduce cluster k8s %s", name)
                                  
                size = 0

                request = self.instanceGroupManagers().resize(project=project, zone=zone, instanceGroupManager=name, size=size)
                response = request.execute()
                    
            request = self.instanceGroupManagers().list_next(previous_request=request, previous_response=response)
                
    # Start
    # Recherche de tous les groupes d'instance du projet pour la zone.
    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def start_k8s(self, project, zone):
        request = self.instanceGroupManagers().list(project=project, zone=zone)
        while request is not None:
            response = request.execute()
            for instance_group_manager in response['items']:
                name = instance_group_manager['baseInstanceName']
                name = "%s-grp"%(name)
                logging.debug("Augment cluster k8s %s", name)
                    
                size = 1

                request = self.instanceGroupManagers().resize(project=project, zone=zone, instanceGroupManager=name, size=size)
                response = request.execute()
                    
            request = self.instanceGroupManagers().list_next(previous_request=request, previous_response=response)