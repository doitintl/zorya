"""Interactions with compute engine."""
import logging

from google.auth import app_engine
from googleapiclient import discovery
from util import gcp

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

CREDENTIALS = app_engine.Credentials(scopes=SCOPES)


class Compute(object):
    """Compute engine actions."""

    def __init__(self, project):
        self.compute = discovery.build(
            'compute', 'v1', credentials=CREDENTIALS)
        self.project = project

    def change_status(self, to_status, tagkey, tagvalue):
        filter = "labels." + tagkey + "=" + tagvalue
        for zone in gcp.get_zones():
            instances = self.list_instances(zone, filter)
            for instance in instances:
                if to_status == 1:
                    logging.info(
                        "Starting %s in project %s tagkey %s tgavalue %s",
                        instance['name'], self.project, tagkey, tagvalue)
                    self.start_instance(zone, instance['name'])
                else:
                    logging.info(
                        "Stopping %s in project %s tagkey %s tgavalue %s",
                        instance['name'], self.project, tagkey, tagvalue)
                    self.stop_instance(zone, instance['name'])
        return 'ok', 200

    def stop_instance(self, zone, instance):
        # TODO add requestId
        res = self.compute.instances().stop(
            project=self.project, zone=zone, instance=instance).execute()
        print res

    def start_instance(self, zone, instance):
        # TODO add requestId
        self.compute.instances().start(
            project=self.project, zone=zone, instance=instance).execute()

    def list_instances(self, zone, filter=None):
        result = self.compute.instances().list(
            project=self.project, zone=zone, filter=filter).execute()
        if 'items' in result:
            return result['items']
        else:
            return []
