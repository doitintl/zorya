"""Change a state for all matching instances in a project."""
import logging

from gcp.compute import Compute
from gcp.sql import Sql
from gcp.stopstartk8s import Stopstartk8s


def change_state(tagkey, tagvalue, action, project):
    """
    Change a state for all matching instances in a project.
    Args:
        tagkey: tag key
        tagvalue: tag value
        action: stop 0 start 1
        project: project id

    Returns:

    """

    compute = Compute(project)
    sql = Sql(project)
    stopstartk8s = Stopstartk8s(project)
    logging.debug("change_state %s action %s", project, action)
    compute.change_status(action, tagkey, tagvalue)
    sql.change_status(action, tagkey, tagvalue)
    stopstartk8s.change_status(action, tagkey, tagvalue)
    return 'ok', 200
