"""Zoyra Worker"""
import os
from fastapi.params import Depends

import google.auth
from fastapi import FastAPI, Request, responses
from fastapi.exceptions import RequestValidationError


_, PROJECT = google.auth.default()
os.environ["ZORYA_PROJECT"] = PROJECT

from zorya.worker.logging import Logger  # noqas
from zorya.worker.logged_route import LoggedRoute  # noqa
from zorya.worker.tasks import policy_tasks, schedule_tasks  # noqa
from zorya.model.state_change import StateChange  # noqa
from zorya.model.pubsub import PubSubEnvelope  # noqa

app = FastAPI()
app.router.route_class = LoggedRoute


def pubsub_state_change(pubsub_envelope: PubSubEnvelope):
    return StateChange(**pubsub_envelope.message.payload_json)


def request_logger(request: Request):
    return Logger(request=request)


@app.post("/tasks/change_state")
def change_state(
    logger: Logger = Depends(request_logger),
    state_change: StateChange = Depends(pubsub_state_change),
):
    """
    Initiate change state.
    """
    logger = logger.refine(state_change=state_change.dict())

    schedule_tasks.change_state(
        **{**state_change.dict(), "project": "chris-playground-297209"},
        logger=logger,
    )
    return


@app.get("/tasks/schedule")
def schedule(request: Request):
    """
    Checks if it's time to run a schedule.
    """
    policy_tasks.check_all(request)
    return


@app.exception_handler(RequestValidationError)
async def log_all_exceptions(request, exception):
    request.state.logger(
        "request validation error",
        detail=exception.errors(),
    )
    return responses.JSONResponse(
        {"detail": exception.errors()}, status_code=422
    )
