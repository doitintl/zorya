"""Interactions with GKE."""

import backoff
from googleapiclient import discovery
from googleapiclient.errors import HttpError

from zorya.worker.gcp import gcp
from zorya.worker.logging import Logger
from zorya.model.node_pool import NodePoolModel
from zorya.util import utils


class Gke(object):
    """GKE engine actions."""

    def __init__(self, project, logger=None):
        self.gke = discovery.build("container", "v1", cache_discovery=False)
        self.project = project
        self.logger = logger or Logger()

    def change_status(self, action, tagkey, tagvalue):
        clusters = self.list_clusters()
        if not clusters:
            self.logger("skipping state change for GKE clusters")
            return

        self.logger(f"running state change for {len(clusters)} GKE clusters")

        for cluster in clusters:
            process_cluster(cluster, action, tagkey, tagvalue, self.logger)

        return

    @backoff.on_exception(
        backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code
    )
    def list_clusters(self):
        """
        List all clusters with the requested tags
        Args:
            zone: zone
            tags_filter: tags

        Returns:

        """
        parent = f"projects/{self.project}/locations/-"
        result = (
            self.gke.projects()
            .locations()
            .clusters()
            .list(parent=parent)
            .execute()
        )

        return result.get("clusters", [])


def process_cluster(cluster, action, tagkey, tagvalue, logger):
    logger = logger.refine(cluster=cluster)

    if not (
        "resourceLabels" in cluster
        and tagkey in cluster["resourceLabels"]
        and cluster["resourceLabels"][tagkey] == tagvalue
    ):
        logger("skipping unmatched cluster")
        return

    for nodePool in cluster["nodePools"]:
        for instanceGroup in nodePool["instanceGroupUrls"]:
            logger = logger.refine(
                nodePool=nodePool, instanceGroup=instanceGroup
            )
            process_instanceGroup(action, instanceGroup, logger)


def process_instanceGroup(action, url, logger):
    if int(action) == 1:
        logger("Sizing up node pool")
        size_up(url)

    else:
        logger("Sizing down node pool")
        size_down(url)


def size_up(url):
    node_pool = NodePoolModel.get_by_url(url)

    if not node_pool.exists:
        return

    num_nodes = node_pool.num_nodes
    gcp.resize_node_pool(num_nodes, url)
    node_pool.delete()


def size_down(url):
    no_of_nodes = gcp.get_instancegroup_no_of_nodes_from_url(url)
    if no_of_nodes == 0:
        return

    node_pool = NodePoolModel.get_by_url(url)
    node_pool = node_pool.set()
    gcp.resize_node_pool(0, url)


def get_instancegroup_no_of_nodes_from_url(url):
    """
    Get no of instances in a group.

    :return: number
    """
    compute = discovery.build("compute", "v1", cache_discovery=False)
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
    """
    compute = discovery.build("compute", "v1", cache_discovery=False)
    url = url[47:]
    project = url[: url.find("/")]
    zone = url[
        url.find("zones") + 6 : url.find("instanceGroupManagers") - 1  # noqa
    ]
    instance_group_manager = url[url.rfind("/") + 1 :]  # noqa

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

    return res
