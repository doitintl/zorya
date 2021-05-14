"""Interactions with GKE."""
import re
import backoff
import google.auth
from requests.exceptions import HTTPError

from zorya.logging import Logger
from zorya.model.node_pool import NodePoolModel
from zorya.resources.utils import fatal_code
from zorya.model.state_change import StateChange

INSTANCE_GROUP_URL_PATTERN = re.compile(
    r"https:\/\/www.googleapis.com\/compute\/v1"
    r"\/projects\/(?P<project>.*)"
    r"\/zones\/(?P<zone>.*)"
    r"\/instanceGroupManagers\/(?P<instance_group_manager>[^\/#?]*)"
)


class GoogleKubernetesEngine(object):
    """GKE engine actions."""

    def __init__(self, state_change: StateChange, logger: Logger = None):
        self.state_change = state_change
        self.logger = logger or Logger()

        credentials, _ = google.auth.default()
        self.authed_session = google.auth.AuthorizedSession(credentials)

        self.clusters = self.list_clusters()

    def change_status(self):
        self.logger(
            f"running state change for {len(self.clusters)} GKE clusters"
        )

        for cluster in self.clusters:
            self.process_cluster(cluster, self.logger)

    def process_cluster(self, cluster, logger):
        logger = logger.refine(cluster=cluster)

        for nodePool in cluster["nodePools"]:
            for instance_group_url in nodePool["instanceGroupUrls"]:
                logger = logger.refine(
                    nodePool=nodePool,
                    instanceGroupUrl=instance_group_url,
                )
                self.process_instance_group(instance_group_url, logger)

    def process_instance_group(self, instance_group_url, logger):
        if int(self.state_change.action) == 1:
            logger("Sizing up node pool")
            self.size_up_instance_group(instance_group_url)

        else:
            logger("Sizing down node pool")
            self.size_down_instance_group(instance_group_url)

    def size_up_instance_group(self, instance_group_url):
        node_pool = NodePoolModel.get_by_url(instance_group_url)

        if not node_pool.exists:
            return

        self.resize_node_pool(node_pool.num_nodes, instance_group_url)
        node_pool.delete()

    def size_down_instance_group(self, instance_group_url):
        num_nodes = self.get_instancegroup_num_nodes_from_url(
            instance_group_url
        )
        if num_nodes == 0:
            return

        node_pool = NodePoolModel.get_by_url(instance_group_url)
        node_pool.num_nodes = num_nodes
        node_pool = node_pool.set()
        self.resize_node_pool(0, instance_group_url)

    def match_cluster(self, cluster):
        return not (
            "resourceLabels" in cluster
            and self.state_change.tagkey in cluster["resourceLabels"]
            and cluster["resourceLabels"][self.state_change.tagkey]
            == self.state_change.tagvalue
        )

    @backoff.on_exception(
        backoff.expo, HTTPError, max_tries=8, giveup=fatal_code
    )
    def list_clusters(self):
        result = self.authed_session.get(
            "https://container.googleapis.com/v1/projects/"
            f"{self.state_change.project}/locations/-/clusters"
        )

        return [
            x
            for x in result.json().get("clusters", [])
            if self.match_cluster(x)
        ]

    @backoff.on_exception(
        backoff.expo, HTTPError, max_tries=8, giveup=fatal_code
    )
    def get_instancegroup_num_nodes_from_url(self, instance_group_url):
        res = self.authed_session.get(instance_group_url)

        res.raise_for_status()
        return res.json().get("size", 0)

    @backoff.on_exception(
        backoff.expo, HTTPError, max_tries=8, giveup=fatal_code
    )
    def resize_node_pool(self, size, instance_group_url):
        """
        resize a node pool
        Args:
            size: requested size
            url: instance group url
        """

        res = self.authed_sessions.post(
            f"{instance_group_url}/resize?size={size}",
        )
        res.raise_for_status()
