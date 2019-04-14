"""Interactions with compute engine."""
import logging

import backoff
from google.auth import app_engine
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from util import gcp, utils

from pprint import pprint

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

CREDENTIALS = app_engine.Credentials(scopes=SCOPES)

class Stopstartk8s(object):
    """Compute engine actions."""

    def __init__(self, project):
        self.compute = discovery.build('compute', 'v1', credentials=CREDENTIALS)
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
        global zone
        zone = str()
        tag_filter = "labels." + tagkey + "=" + tagvalue
        logging.debug("Filter %s", filter)
        for zone in gcp.get_zones():
            if int(to_status) == 1:
                #zone = 'europe-west1-b'
                logging.debug("FCT change_status : Augment k8s cluster pour project %s dans la zone %s", self.project, zone)
                self.start_k8s(zone)
            else:
                #zone = 'europe-west1-b'
                logging.debug("FCT change_status : Reduce k8s cluster pour project %s dans la zone %s", self.project, zone)
                self.stop_k8s(zone)
        return 'ok', 200
         
        
    # Arret
    # Recherche de tous les groupes d'instance du projet pour la zone.
    @backoff.on_exception(backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def stop_k8s(self, zone):
        #zone = 'europe-west1-b'
        logging.debug("FCT stop_k8s : Search k8s cluster on project %s in zone %s", self.project, zone)
        request = self.compute.instanceGroupManagers().list(project=self.project, zone=zone)
        while request is not None:
            response = request.execute()
            if 'items' in response:
                for instance_group_manager in response['items']:
                    name = instance_group_manager['name']
                    #name = "%s-grp"%(name)
                    print(name)
                                    
                    #size = 1
                    logging.debug("FCT stop_k8s : Reduce cluster k8s %s on project %s to 0", name, self.project)

                    request = self.compute.instanceGroupManagers().resize(project=self.project, zone=zone, instanceGroupManager=name, size=0)
                    response = request.execute()
                    
                request = self.compute.instanceGroupManagers().list_next(previous_request=request, previous_response=response)
            else:
                logging.debug("FCT stop_k8s : No cluster k8s on project %s in zone %s", self.project, zone)
                
    # Start
    # Recherche de tous les groupes d'instance du projet pour la zone.
    @backoff.on_exception(backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def start_k8s(self, zone):
        #zone = 'europe-west1-b'
        logging.debug("FCT start_k8s : Search k8s cluster on project %s in zone %s", self.project, zone)
        request = self.compute.instanceGroupManagers().list(project=self.project, zone=zone)
        #request = self.compute.instanceGroupManagers().list(project=self.project, zone=zone)
        while request is not None:
            response = request.execute()
            if 'items' in response:
                for instance_group_manager in response['items']:
                    name = instance_group_manager['name']
                    #name = "%s-grp"%(name)
                    print(name)
                                    
                    #size = 1
                    logging.debug("FCT start_k8s : Augment cluster k8s %s on project %s to 1", name, self.project)

                    request = self.compute.instanceGroupManagers().resize(project=self.project, zone=zone, instanceGroupManager=name, size=1)
                    #request = self.compute.instanceGroupManagers().resize(project=self.project, zone=zone, instanceGroupManager=name, size=1)
                    response = request.execute()
                    
                request = self.compute.instanceGroupManagers().list_next(previous_request=request, previous_response=response)
            else:
                logging.debug("FCT stop_k8s : No cluster k8s on project %s in zone %s", self.project, zone)