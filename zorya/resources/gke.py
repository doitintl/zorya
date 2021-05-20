"""Interactions with GKE."""
from typing import Generator

from zorya.logging import Logger
from zorya.resources.gcp_base import GCPBase
from zorya.models.gke_node_pool import GKENodePool
from zorya.models.gke_cluster import GoogleKubernetesEngineCluster


class GoogleKubernetesEngine(GCPBase):
    """GKE engine actions."""

    def change_status(self) -> None:
        self.logger("running state change for GKE clusters")

        for cluster in self.list_clusters():
            self.process_cluster(cluster, self.logger)

    def list_clusters(
        self,
    ) -> Generator[GoogleKubernetesEngineCluster, None, None]:
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

    def process_cluster(
        self, cluster: GoogleKubernetesEngineCluster, logger: Logger
    ) -> None:
        logger = logger.refine(cluster=cluster)

        if int(self.state_change.action) == 1:
            action = self.size_up_node_pool
        else:
            action = self.size_down_node_pool

        for nodePool in cluster.nodePools:
            for instance_group_url in nodePool.instanceGroupUrls:
                logger = logger.refine(
                    nodePool=nodePool, instanceGroupUrl=instance_group_url
                )
                action(instance_group_url, logger)

    def size_up_node_pool(
        self, instance_group_url: str, logger: Logger
    ) -> None:
        node_pool = GKENodePool.get_by_url(instance_group_url)

        if not node_pool.exists:
            return

        self.resize_node_pool(node_pool.num_nodes, instance_group_url, logger)
        node_pool.delete()

    def size_down_node_pool(
        self, instance_group_url: str, logger: Logger
    ) -> None:
        num_nodes = self.get_instancegroup_num_nodes(
            instance_group_url, logger
        )
        if num_nodes == 0:
            return

        node_pool = GKENodePool.get_by_url(instance_group_url)
        node_pool.num_nodes = num_nodes
        node_pool.set()
        self.resize_node_pool(0, instance_group_url, logger)

    def resize_node_pool(
        self, size: int, instance_group_url: str, logger: Logger
    ) -> None:
        res = self.authed_session.post(
            f"{instance_group_url}/resize?size={size}"
        )
        if res.status_code >= 400:
            logger("failed resizing node pool", error=res.json())

    def match_cluster(self, cluster: GoogleKubernetesEngineCluster) -> bool:
        return (
            self.state_change.tagkey in cluster.resourceLabels
            and cluster.resourceLabels[self.state_change.tagkey]
            == self.state_change.tagvalue
        )

    def get_instancegroup_num_nodes(
        self, instance_group_url, logger: Logger
    ) -> int:
        res = self.authed_session.get(instance_group_url)

        if res.status_code >= 400:
            logger("failed fetching current node pool size", error=res.json())
            return 0

        return res.json().get("size", 0)
