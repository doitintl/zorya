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
        logging.info("GKE change_status")        
        client = ndb.Client()
        with client.context():
            try:
                logging.info("List cluster")
                # List all the clusters in the project
                clusters = self.list_clusters()
                # Considering one cluster at a time
                for cluster in clusters:
                    logging.info("Cluster location " + cluster["location"])
                    # Check if the cluster has to be managed
                    if (
                        "resourceLabels" in cluster
                        and tagkey in cluster["resourceLabels"]
                        and cluster["resourceLabels"][tagkey] == tagvalue
                    ):
                        logging.info("GKE change_status cluster %s %s %s", cluster,cluster["resourceLabels"],cluster["resourceLabels"][tagkey])
                        # Considering one node pool at a time for a specific cluster
                        for nodePool in cluster["nodePools"]:
                            logging.info("extract number of nodes")
                            logging.info(cluster["location"])
                            logging.info(nodePool["instanceGroupUrls"])
                            # Sizing up
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
                                # Query Datastore to get the number of nodes of the specific node pool
                                res = GkeNodePoolModel.query(
                                    GkeNodePoolModel.Name == nodePool["name"]
                                ).get()
                                logging.info(res)
                                # If the node pool is not on Datastore, pass-by
                                if not res:
                                    continue
                                # Call the function to size up the node pool, we pass the number of nodes read on Datastore (res.NumberOfNodes)
                                gcp.resize_node(self.project, cluster["name"], nodePool["name"], cluster["location"], res.NumberOfNodes)
                                # Clear the information on Datastore
                                res.key.delete()
                            # Sizing down
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
                                # Valorizing variables to put on Datastore
                                node_pool_model = GkeNodePoolModel()
                                node_pool_model.Name = nodePool["name"]
                                no_of_nodes=0
                                # Check one instance group at a time for a specific node pool, to count the total number of nodes
                                for instanceGroup in nodePool["instanceGroupUrls"]:
                                    logging.info("Counting instanceGroups")
                                    url = instanceGroup
                                    # (get_instancegroup_no_of_nodes_from_url) returns the size of an instance group
                                    no_of_nodes_inst_group = gcp.get_instancegroup_no_of_nodes_from_url(url)
                                    # Sum the size of an instance group to the total number of nodes
                                    no_of_nodes += no_of_nodes_inst_group
                                logging.info(no_of_nodes)    
                                # Check if the cluster is regional or not. (cluster["location"]) returns a region if
                                # the cluster is regional, or a zone if it's not
                                if gcp.is_regional(cluster["location"]): 
                                    logging.info("cluster is regional")
                                    # (num_zones) is the number of zones in the region we are considering.
                                    # please note: (cluster["locations"]) returns a list of zones, unlike (cluster["location"])
                                    num_zones = len(cluster["locations"])
                                    # Divide (no_of_nodes) for (num_zones) to get the number of nodes per zone.
                                    # this has to be done because the API call for sizing up needs this parameter,
                                    # otherwise the node pool grows uncontrollably.
                                    no_of_nodes = int(no_of_nodes/num_zones)
                                    logging.info(no_of_nodes)
                                # If the cluster is not regional we took (no_of_nodes) without dividing it for (num_zones)
                                else:
                                    logging.info("cluster is not regional")
                                if no_of_nodes == 0:
                                   continue
                                logging.info("number of nodes")
                                logging.info(no_of_nodes)
                                # Valorizing variables and putting them on Datastore
                                node_pool_model.NumberOfNodes = no_of_nodes
                                node_pool_model.key = ndb.Key(
                                    "GkeNodePoolModel", nodePool["name"]
                                )
                                node_pool_model.put()
                                # Sizing down node pool, in this case the number of nodes we pass is zero
                                gcp.resize_node(self.project, cluster["name"], nodePool["name"], cluster["location"], 0)
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

