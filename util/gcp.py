
""""GCP utils"""
import googleapiclient.discovery
from google.auth import app_engine
from util import utils



SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
CREDENTIALS = app_engine.Credentials(scopes=SCOPES)


def get_regions():
    """
    Get all available regions.

    :return: all regions
    """
    compute = googleapiclient.discovery.build('compute', 'v1')

    request = compute.regions().list(project=utils.get_project_id())

    response = request.execute()
    rg = []
    for region in response['items']:
        rg.append(region['description'])
    return rg


def get_zones():
    """
    Get all available zones.

    :return: all regions
    """
    compute = googleapiclient.discovery.build('compute', 'v1')

    request = compute.zones().list(project=utils.get_project_id())

    response = request.execute()
    zones = []
    for region in response['items']:
        zones.append(region['description'])
    return zones
