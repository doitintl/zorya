"""Zoyra Worker"""
import os
import logging

import google.auth
from fastapi import FastAPI

from zorya.worker.tasks import policy_tasks, schedule_tasks
from zorya.model.state_change import StateChange

_, PROJECT = google.auth.default()
os.environ["ZORYA_PROJECT"] = PROJECT

app = FastAPI()


@app.post("/tasks/change_state")
def change_state(state_change: StateChange):
    """
    Initiate change state.
    """
    logging.debug("Starting change_state action {state_change}")
    schedule_tasks.change_state(**state_change)
    return


@app.get("/tasks/schedule")
def schedule():
    """
    Checks if it's time to run a schedule.
    Returns:

    """
    logging.debug("From Cron start /tasks/schedule")

    policy_tasks.check_all()
    return


if __name__ == "__main__":
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.INFO)
    app.run(debug=False)
