"""Interactions with compute engine."""
import logging

import backoff
from google.auth import app_engine
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from util import gcp, utils

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
            try:
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
            except HttpError as http_error:
                logging.error(http_error)
                return 'Error', 500
        return 'ok', 200

    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def stop_instance(self, zone, instance):
        # TODO add requestId
        return self.compute.instances().stop(
            project=self.project, zone=zone, instance=instance).execute()

    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def start_instance(self, zone, instance):
        # TODO add requestId
        return self.compute.instances().start(
            project=self.project, zone=zone, instance=instance).execute()

    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
    def list_instances(self, zone, filter=None):
        result = self.compute.instances().list(
            project=self.project, zone=zone, filter=filter).execute()
        if 'items' in result:
            return result['items']
        else:
            return []
