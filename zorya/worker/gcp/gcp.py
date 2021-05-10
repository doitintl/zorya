""""GCP utils"""
import os
import logging

import backoff
import googleapiclient.discovery
from googleapiclient.errors import HttpError

from zorya.util import utils


def get_regions():
    """
    Get all available regions.

    :return: all regions
    """
    compute = googleapiclient.discovery.build(
        "compute", "v1", cache_discovery=False
    )

    request = compute.regions().list(project=os.environ["ZORYA_PROJECT"])

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
    compute = googleapiclient.discovery.build(
        "compute", "v1", cache_discovery=False
    )

    request = compute.zones().list(project=os.environ["ZORYA_PROJECT"])

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
    compute = googleapiclient.discovery.build(
        "compute", "v1", cache_discovery=False
    )
    url = url[47:]
    project = url[: url.find("/")]
    zone = url[
        url.find("zones") + 6 : url.find("instanceGroupManagers") - 1  # noqa
    ]
    pool = url[url.rfind("/") + 1 :]  # noqa
    res = (
        compute.instanceGroups()
        .get(project=project, zone=zone, instanceGroup=pool)
        .execute()
    )
    return res["size"]


@backoff.on_exception(
    backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code
)
def resize_node_pool(size, url):
    """
    resize a node pool
    Args:
        size: requested size
        url: instance group url

    Returns:

    """
    compute = googleapiclient.discovery.build(
        "compute", "v1", cache_discovery=False
    )
    url = url[47:]
    project = url[: url.find("/")]
    zone = url[
        url.find("zones") + 6 : url.find("instanceGroupManagers") - 1  # noqa
    ]
    instance_group_manager = url[url.rfind("/") + 1 :]  # noqa
    try:
        res = (
            compute.instanceGroupManagers()
            .resize(
                project=project,
                zone=zone,
                instanceGroupManager=instance_group_manager,
                size=size,
            )
            .execute()
        )
    except Exception as e:
        logging.error(e)
    return res
