"""Change a state for all matching instances in a project."""
from zorya.worker.gcp.compute import Compute
from zorya.worker.gcp.sql import Sql
from zorya.worker.gcp.gke import Gke


def change_state(*, tagkey, tagvalue, action, project, logger):
    """
    Change a state for all matching instances in a project.
    Args:
        tagkey: tag key
        tagvalue: tag value
        action: stop 0 start 1
        project: project id
    """
    compute = Compute(project, logger=logger)
    sql = Sql(project, logger=logger)
    gke = Gke(project, logger=logger)

    compute.change_status(action, tagkey, tagvalue)
    sql.change_status(action, tagkey, tagvalue)
    gke.change_status(action, tagkey, tagvalue)
    return "ok", 200
