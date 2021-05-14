"""Change a state for all matching instances in a project."""
from zorya.resources.gke import GoogleKubernetesEngine
from zorya.resources.cloud_sql import CloudSql
from zorya.resources.gce import GoogleComputEngine


def change_state(state_change, logger=None):
    """
    Change a state for all matching instances in a project.
    Args:
        tagkey: tag key
        tagvalue: tag value
        action: stop 0 start 1
        project: project id
    """
    GoogleComputEngine(state_change, logger=logger).change_status()

    CloudSql(state_change, logger=logger).change_status()

    GoogleKubernetesEngine(state_change, logger=logger).change_status()
