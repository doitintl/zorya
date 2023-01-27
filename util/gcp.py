""""GCP utils"""

import logging

import backoff
import googleapiclient.discovery
import time
from googleapiclient.errors import HttpError
from util import utils


def get_regions():
    """
    Get all available regions.

    :return: all regions
    """
    compute = googleapiclient.discovery.build("compute", "v1", cache_discovery=False)

    request = compute.regions().list(project=utils.get_project_id())

    response = request.execute()
    rg = []
    for region in response["items"]:
        rg.append(region["description"])
    return rg


def get_zones():
    """
    Get all available zones.

    :return: all regions
    """
    compute = googleapiclient.discovery.build("compute", "v1", cache_discovery=False)

    request = compute.zones().list(project=utils.get_project_id())

    response = request.execute()
    zones = []
    for region in response["items"]:
        zones.append(region["description"])
    return zones


def get_instancegroup_no_of_nodes_from_url(url):
    """
    Get no of instances in a group.

    :return: number
    """
    compute = googleapiclient.discovery.build("compute", "v1", cache_discovery=False)
    url = url[47:]
    project = url[: url.find("/")]
    zone = url[url.find("zones") + 6 : url.find("instanceGroupManagers") - 1]
    pool = url[url.rfind("/") + 1 :]
    res = (
        compute.instanceGroups()
        .get(project=project, zone=zone, instanceGroup=pool)
        .execute()
    )
    return res["size"]


@backoff.on_exception(backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
def resize_node(project_id, cluster_id, node_pool_id, location, node_pool_size):

    # This function handles gke clusters with one or more node pools. Scaling more than one node pool in a cluster
    # at the same time generates an error in gcp, this particular error is set as a warning in the except section.
    # API: https://cloud.google.com/kubernetes-engine/docs/reference/rest/v1/projects.locations.clusters.nodePools/setSize

    service = googleapiclient.discovery.build('container', 'v1', cache_discovery=False)

    # Parameters for the while cycle
    max_retry=7
    count=0
    response = None

    # Parameters for the API call
    name="projects/%s/locations/%s/clusters/%s/nodePools/%s" % (project_id, location, cluster_id, node_pool_id)
    body={"nodeCount":node_pool_size}

    # In case of exception 'response' remain equals to None. We retry the resize for 7 times in a total time of 21 minues.
    # When the previous node pool completes the resize, 'response' stops going in exception and returns a value != None
    while response == None and count < max_retry:
        try:
            response = (service.projects().locations().clusters().nodePools().setSize(name=name, body=body).execute())

        except Exception as e:
            # Setting the specific error as warning.
            # At least one of this warning logs will appear in case of multiple node pools.
            if(str('currently operating on cluster ' + cluster_id + '. Please wait and try again once it is done.') in str(e.content)):
                logging.warning(e)
            else:
                logging.error(e)
            count += 1
            # Wait 3 minutes for the precedent node pool to finish the resize before retry. Generate less warning logs
            time.sleep(180)
    return response


def is_regional(location):

# Check if the cluster is regional. We pass (cluster["location"]) as parameter, that is a region or a zone.
# every region name in gcp ends with a number and every zone name ends with a letter.

    if location.endswith(("0","1","2","3","4","5","6","7","8","9")): 
        return True
    else:
        return False     