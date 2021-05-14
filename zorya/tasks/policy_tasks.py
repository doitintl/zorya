"""Check if there is a need to take an action for a policy."""
import json

import google.auth
from google.cloud import pubsub

from zorya.model.policy import Policy
from zorya.model.schedule import Schedule
from zorya.settings import settings


TASK_TOPIC = "zorya"


def check_all(logger):
    for policy in Policy.list():
        check_one(policy, logger.refine(policy=policy.dict()))


def check_one(policy, logger):
    """
    Check if there is a need to take an action for a policy.
    Args:
        name: policy
    """
    logger("checking policy")
    schedule = Schedule.get_by_name(policy.schedulename)
    if not schedule.exists:
        logger("schedule {policy.schedulename} not found!")
        return

    logger = logger.refine(schedule=schedule.dict())
    if schedule.changed:
        logger("conditions are met, nothing to do")
        return

    logger(f"state is changing to {schedule.desired_state}")

    credentials, _ = google.auth.default()

    publisher = pubsub.PublisherClient(credentials=credentials)
    topic_name = f"projects/{settings.project_id}/topics/{settings.topic_id}"

    futures = []

    for tagkeyvalue in policy.tags:
        tagkey, tagvalue = tagkeyvalue.popitem()

        for project in policy.projects:
            payload = {
                "project": project,
                "tagkey": tagkey,
                "tagvalue": tagvalue,
                "action": schedule.desired_state,
            }

            logger("inserting task", payload=payload)

            future = publisher.publish(
                topic_name,
                data=json.dumps(payload).encode("utf-8"),
            )

            futures.append(future)

    for future in futures:
        future.result()
