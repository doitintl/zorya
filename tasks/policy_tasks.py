"""Check if there is a need to take an action for a policy."""
import json
import logging

import numpy as np
from google.cloud import ndb, tasks_v2
from model.policymodel import PolicyModel
from model.schedulesmodel import SchedulesModel
from util import location, tz, utils


def policy_checker(name):
    """
    Check if there is a need to take an action for a policy.
    Args:
        name: policy name
        context

    Returns:

    """

    policy = PolicyModel.query(PolicyModel.Name == name).get()
    if not policy:
        logging.error("Policy %s not found!", name)
        return "not found", 404
    schedule = SchedulesModel.query(SchedulesModel.Name == policy.Schedule).get()
    if not schedule:
        logging.error("Schedule %s not found!", policy.Schedule)
        return "not found", 404
    logging.debug(
        "Time at Timezone %s is %s",
        schedule.Timezone,
        tz.get_time_at_timezone(schedule.Timezone),
    )
    day, hour = tz.convert_time_to_index(tz.get_time_at_timezone(schedule.Timezone))
    logging.debug("Working on day  %s hour  %s", day, hour)
    arr = np.asarray(schedule.Schedule["__ndarray__"], dtype=np.int).flatten()
    matrix_size = schedule.Schedule["Shape"][0] * schedule.Schedule["Shape"][1]
    prev = utils.get_prev_idx(day * 24 + hour, matrix_size)
    now = arr[day * 24 + hour]
    prev = arr[prev]
    logging.debug("Previous state %s current %s", prev, now)
    if now == prev:
        # do nothing
        logging.info("Nothing should be done for %s", name)
        return "ok", 200
    else:
        # stop/start
        logging.info("State is changing for %s to %s", name, now)
        # for each tag lets do it

        task_client = tasks_v2.CloudTasksClient()
        task = {
            "app_engine_http_request": {  # Specify the type of request.
                "http_method": "POST",
                "relative_uri": "/tasks/change_state",
            }
        }
        parent = task_client.queue_path(
            queue="zorya-tasks",
            project=utils.get_project_id(),
            location=location.get_location(),
        )
        for tag in policy.Tags:
            for project in policy.Projects:
                payload = {
                    "project": project,
                    "tagkey": next(iter(tag)),
                    "tagvalue": tag[next(iter(tag))],
                    "action": str(now),
                }
                task["app_engine_http_request"]["body"] = (
                    json.dumps(payload)
                ).encode()
                response = task_client.create_task(parent, task)
                logging.debug("Task %s enqueued", response.name)
    return "ok", 200
