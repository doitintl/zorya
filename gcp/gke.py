"""Interactions with GKE."""

import logging

import backoff
from google.cloud import ndb
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from model.gkenoodespoolsmodel import GkeNodePoolModel
from util import gcp, utils

CREDENTIALS = None


class Gke(object):
    """GKE engine actions."""

    def __init__(self, project):
        self.gke = discovery.build("container", "v1", cache_discovery=False)
        self.project = project

    def change_status(self, to_status, tagkey, tagvalue):
        try:
            clusters = self.list_clusters()
            for cluster in clusters:
                if (
                    "resourceLabels" in cluster
                    and tagkey in cluster["resourceLabels"]
                    and cluster["resourceLabels"][tagkey] == tagvalue
                ):
                    for nodePool in cluster["nodePools"]:
                        logging.debug(nodePool["instanceGroupUrls"])
                        for instanceGroup in nodePool["instanceGroupUrls"]:
                            url = instanceGroup
                            logging.debug(url)
                            node_pool_name = url[url.rfind("/") + 1 :]
                            no_of_nodes = gcp.get_instancegroup_no_of_nodes_from_url(
                                url
                            )
                            if int(to_status) == 1:
                                logging.info(
                                    "Sizing up node pool %s in cluster %s "
                                    "tagkey "
                                    "%s tagvalue %s",
                                    nodePool["name"],
                                    cluster["name"],
                                    tagkey,
                                    tagvalue,
                                )
                                res = GkeNodePoolModel.query(
                                    GkeNodePoolModel.Name == node_pool_name
                                ).get()
                                logging.debug(res)
                                if not res:
                                    continue
                                gcp.resize_node_pool(res.NumberOfNodes, url)
                                res.key.delete()
                            else:
                                logging.info(
                                    "Sizing down node pool %s in cluster %s "
                                    "tagkey "
                                    "%s tagvalue %s",
                                    nodePool["name"],
                                    cluster["name"],
                                    tagkey,
                                    tagvalue,
                                )
                                if no_of_nodes == 0:
                                    continue
                                node_pool_model = GkeNodePoolModel()
                                node_pool_model.Name = node_pool_name
                                node_pool_model.NumberOfNodes = no_of_nodes
                                node_pool_model.key = ndb.Key(
                                    "GkeNodePoolModel", node_pool_name
                                )
                                node_pool_model.put()
                                gcp.resize_node_pool(0, url)
        except HttpError as http_error:
            logging.error(http_error)
            return "Error", 500
        return "ok", 200

    @backoff.on_exception(backoff.expo, HttpError, max_tries=8, giveup=utils.fatal_code)
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
            self.gke.projects().locations().clusters().list(parent=parent).execute()
        )
        if "clusters" in result:
            return result["clusters"]
        else:
            return []
