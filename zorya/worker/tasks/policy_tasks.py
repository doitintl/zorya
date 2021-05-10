"""Check if there is a need to take an action for a policy."""
import json
import logging

import numpy as np
import google.auth
from google.cloud import pubsub

from zorya.model.policymodel import PolicyModel
from zorya.model.schedulesmodel import SchedulesModel
from zorya.util import tz, utils

MATRIX_SIZE = 7 * 24
TASK_TOPIC = "zorya_tasks"


def check_all():
    for policy in PolicyModel.list():
        check_one(policy)


def check_one(policy):
    """
    Check if there is a need to take an action for a policy.
    Args:
        name: policy
    """
    schedule = SchedulesModel.get_by_name(policy.schedulename)
    if not schedule.exists:
        logging.error("Schedule %s not found!", policy.schedulename)
        return "not found", 404

    local_time = tz.get_time_at_timezone(schedule.timezone)
    logging.debug("Time at Timezone %s is %s", schedule.timezone, local_time)

    day, hour = tz.convert_time_to_index(local_time)
    logging.debug("Working on day  %s hour  %s", day, hour)

    arr = np.asarray(
        json.loads(schedule["ndarray"]),
        dtype=np.int,
    ).flatten()

    prev = utils.get_prev_idx(day * 24 + hour, MATRIX_SIZE)
    now = arr[day * 24 + hour]
    prev = arr[prev]

    logging.info("Previous state %s current %s", prev, now)
    if now == prev:
        logging.info(
            "Conditions are met, Nothing should be done for %s", policy.name
        )
        return "ok", 200

    logging.info("State is changing for %s to %s", policy.name, now)

    credentials, project_id = google.auth.default()
    publisher = pubsub.PublisherClient(
        credentials=credentials, project=project_id
    )
    topic_name = f"projects/{project_id}/topics/{TASK_TOPIC}"

    futures = []

    for tagkey, tagvalue in policy.tags:
        for project in policy.projects:
            payload = {
                "project": project,
                "tagkey": tagkey,
                "tagvalue": tagvalue,
                "action": str(now),
            }

            future = publisher.publish(
                topic_name,
                data=json.dumps(payload).endcode(),
            )

            futures.append(future)
            logging.debug("Task enqueued")

    for future in futures:
        future.result()

    return "ok", 200
