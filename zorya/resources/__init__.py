from typing import List, Type

from zorya.resources.gcp_base import GCPBase
from zorya.resources.cloud_sql import CloudSql
from zorya.resources.gke import GoogleKubernetesEngine
from zorya.resources.gce import GoogleComputEngine


ALL_RESOURCES: List[Type[GCPBase]] = [
    GoogleKubernetesEngine,
    CloudSql,
    GoogleComputEngine,
]
