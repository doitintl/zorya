"""gke_cluster.py"""
from typing import List, Dict
import pydantic
from zorya.models.gke_node_pool import GKENodePool


class GoogleKubernetesEngineCluster(pydantic.BaseModel):
    name: str
    nodePools: List[GKENodePool]
    resourceLabels: Dict[str, str]
