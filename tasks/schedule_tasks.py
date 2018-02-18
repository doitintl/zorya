"""Change a state for all matching instances in a project."""
from gcp.compute import Compute


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
    compute.change_status(action, tagkey, tagvalue)
    return 'ok', 200
