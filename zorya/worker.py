"""Zoyra Worker"""
import json

from flask import Flask, request

from zorya.tasks import policy_tasks, schedule_tasks

import logging  # noqa

app = Flask(__name__)


@app.route("/tasks/change_state", methods=["POST"])
def change_state():
    """
    Initiate change state.
    """
    payload = json.loads(request.get_data(as_text=False) or "(empty payload)")
    logging.debug(
        "Starting change_state action %s project %s tagkey %s tagvalue %s",
        payload["action"],
        payload["project"],
        payload["tagkey"],
        payload["tagvalue"],
    )
    schedule_tasks.change_state(
        payload["tagkey"],
        payload["tagvalue"],
        payload["action"],
        payload["project"],
    )
    return "ok", 200


@app.route("/tasks/schedule", methods=["GET"])
def schedule():
    """
    Checks if it's time to run a schedule.
    Returns:

    """
    logging.debug("From Cron start /tasks/schedule")

    policy_tasks.check_all()
    return "ok", 200


if __name__ == "__main__":
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.INFO)
    app.run(debug=False)
