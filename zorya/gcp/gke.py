"""Interactions with GKE."""
import logging
from zorya.model.node_pool import NodePoolModel

import backoff
from googleapiclient import discovery
from googleapiclient.errors import HttpError

from zorya.util import gcp, utils

CREDENTIALS = None


class Gke(object):
    """GKE engine actions."""

    def __init__(self, project):
        self.gke = discovery.build("container", "v1", cache_discovery=False)
        self.project = project

    def change_status(self, to_status, tagkey, tagvalue):
        logging.debug("GKE change_status")
        try:
            clusters = self.list_clusters()
            for cluster in clusters:
                process_cluster(cluster, to_status, tagkey, tagvalue)

        except HttpError as http_error:
            logging.error(http_error)
            return "Error", 500
        return "ok", 200

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
        parent = "projects/%s/locations/-" % self.project
        result = (
            self.gke.projects()
            .locations()
            .clusters()
            .list(parent=parent)
            .execute()
        )
        if "clusters" in result:
            return result["clusters"]
        else:
            return []


def process_cluster(cluster, to_status, tagkey, tagvalue):
    if (
        "resourceLabels" in cluster
        and tagkey in cluster["resourceLabels"]
        and cluster["resourceLabels"][tagkey] == tagvalue
    ):
        logging.debug(
            "GKE change_status cluster %s %s %s",
            cluster,
            cluster["resourceLabels"],
            cluster["resourceLabels"][tagkey],
        )
        for nodePool in cluster["nodePools"]:
            logging.debug(nodePool["instanceGroupUrls"])
            for instanceGroup in nodePool["instanceGroupUrls"]:
                process_instanceGroup(
                    to_status,
                    instanceGroup,
                    cluster=cluster,
                    tagkey=tagkey,
                    tagvalue=tagvalue,
                    nodePool=nodePool,
                )


def process_instanceGroup(to_status, url, **kwargs):
    if int(to_status) == 1:
        logging.debug(
            "Sizing up node pool %s in cluster %s " "tagkey " "%s tagvalue %s",
            kwargs["nodePool"]["name"],
            kwargs["cluster"]["name"],
            kwargs["tagkey"],
            kwargs["tagvalue"],
        )
        size_up(url)

    else:
        logging.debug(
            "Sizing down node pool %s in cluster %s tagkey %s tagvalue %s",
            kwargs["nodePool"]["name"],
            kwargs["cluster"]["name"],
            kwargs["tagkey"],
            kwargs["tagvalue"],
        )
        size_down(url)


def size_up(url):
    name = url.split("/")[-1]

    node_pool = NodePoolModel.get_by_name(name)

    if node_pool.exists:
        num_nodes = node_pool.num_nodes
        gcp.resize_node_pool(num_nodes, url)
        node_pool.delete()


def size_down(url):
    name = url.split("/")[-1]
    no_of_nodes = gcp.get_instancegroup_no_of_nodes_from_url(url)
    if no_of_nodes == 0:
        return

    node_pool = NodePoolModel.get_by_name(name)
    node_pool = node_pool.set({"name": name, "no_of_nodes": no_of_nodes})
    gcp.resize_node_pool(0, url)
