"""Change a state for all matching instances in a project."""
import logging

from gcp.compute import Compute
from gcp.sql import Sql
from gcp.gke import Gke
from gcp.gae import Gae


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
    if not (check_if_app_engine_job(tagkey, tagvalue)):
        compute = Compute(project)
        sql = Sql(project)
        gke = Gke(project)
        logging.info("change_state %s action %s", project, action)
        compute.change_status(action, tagkey, tagvalue)
        sql.change_status(action, tagkey, tagvalue)
        gke.change_status(action, tagkey, tagvalue)
    else:
        service_id, version_id = get_service_and_version_from_tag_value(tagvalue)
        app_engine = Gae(project)
        logging.info("change_state %s action %s", project, action)
        app_engine.change_status(action, service_id, version_id)
    return 'ok', 200


def check_if_app_engine_job(tagkey, tagvalue):
    """
    Infer by the tag key and value if its an App Engine job

    Args:
        tagkey: tag key
        tagvalue: tag value

    Returns:
    """

    if (tagkey == '@app_engine_flex') and (':' in tagvalue):
        return True
    else:
        return False


def get_service_and_version_from_tag_value(tagvalue):
    return tagvalue.split(':')

