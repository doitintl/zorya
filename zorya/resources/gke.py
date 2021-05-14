"""Interactions with GKE."""
from typing import List

from zorya.logging import Logger
from zorya.resources.gcp_base import GCPBase
from zorya.model.gke_node_pool import GKENodePool
from zorya.model.gke_cluster import GoogleKubernetesEngineCluster


class GoogleKubernetesEngine(GCPBase):
    """GKE engine actions."""

    def change_status(self) -> None:
        self.logger("running state change for GKE clusters")

        for cluster in self.list_clusters():
            self.process_cluster(cluster, self.logger)

    def process_cluster(
        self,
        cluster: GoogleKubernetesEngineCluster,
        logger: Logger,
    ) -> None:
        logger = logger.refine(cluster=cluster)

        for nodePool in cluster.nodePools:
            for instance_group_url in nodePool.instanceGroupUrls:
                logger = logger.refine(
                    nodePool=nodePool,
                    instanceGroupUrl=instance_group_url,
                )
                self.process_instance_group(instance_group_url, logger)

    def process_instance_group(
        self,
        instance_group_url: str,
        logger: Logger,
    ) -> None:
        if int(self.state_change.action) == 1:
            logger("Sizing up node pool")
            self.size_up_instance_group(instance_group_url)

        else:
            logger("Sizing down node pool")
            self.size_down_instance_group(instance_group_url)

    def size_up_instance_group(
        self,
        instance_group_url: str,
    ) -> None:
        node_pool = GKENodePool.get_by_url(instance_group_url)

        if not node_pool.exists:
            return

        self.resize_node_pool(node_pool.num_nodes, instance_group_url)
        node_pool.delete()

    def size_down_instance_group(
        self,
        instance_group_url: str,
    ) -> None:
        num_nodes = self.get_instancegroup_num_nodes_from_url(
            instance_group_url
        )
        if num_nodes == 0:
            return

        node_pool = GKENodePool.get_by_url(instance_group_url)
        node_pool.num_nodes = num_nodes
        node_pool = node_pool.set()
        self.resize_node_pool(0, instance_group_url)

    def match_cluster(
        self,
        cluster: GoogleKubernetesEngineCluster,
    ) -> bool:
        return not (
            self.state_change.tagkey in cluster.resourceLabels
            and cluster.resourceLabels[self.state_change.tagkey]
            == self.state_change.tagvalue
        )

    def list_clusters(self) -> List[GoogleKubernetesEngineCluster]:
        result = self.authed_session.get(
            "https://container.googleapis.com/v1"
            f"/projects/{self.state_change.project}"
            "/locations/-"
            "/clusters"
        )

        for x in result.json().get("clusters", []):
            cluster = GoogleKubernetesEngineCluster(**x)
            if self.match_cluster(cluster):
                yield cluster

    def get_instancegroup_num_nodes_from_url(
        self,
        instance_group_url,
    ) -> int:
        res = self.authed_session.get(instance_group_url)

        res.raise_for_status()
        return res.json().get("size", 0)

    def resize_node_pool(
        self,
        size: int,
        instance_group_url: str,
    ) -> None:
        res = self.authed_session.post(
            f"{instance_group_url}/resize?size={size}",
        )
        res.raise_for_status()
