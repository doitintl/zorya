"""Change a state for all matching instances in a project."""
import logging

from zorya.gcp.compute import Compute
from zorya.gcp.sql import Sql
from zorya.gcp.gke import Gke


def change_state(tagkey, tagvalue, action, project):
    """
    Change a state for all matching instances in a project.
    Args:
        tagkey: tag key
        tagvalue: tag value
        action: stop 0 start 1
        project: project id
    """
    compute = Compute(project)
    sql = Sql(project)
    gke = Gke(project)
    logging.info("change_state %s action %s", project, action)
    compute.change_status(action, tagkey, tagvalue)
    sql.change_status(action, tagkey, tagvalue)
    gke.change_status(action, tagkey, tagvalue)
    return "ok", 200
