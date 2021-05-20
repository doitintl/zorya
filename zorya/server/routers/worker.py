"""Zoyra Worker"""
from fastapi import APIRouter, Request, Depends

from zorya.models.state_change import StateChange
from zorya.models.pubsub import PubSubEnvelope
from zorya.models.policy import Policy
from zorya.server.logged_route import LoggedRoute
from zorya.logging import Logger
from zorya.settings import settings

router = APIRouter(route_class=LoggedRoute)


def pubsub_state_change(pubsub_envelope: PubSubEnvelope):
    return StateChange(**pubsub_envelope.message.payload_json)


def request_logger(request: Request):
    return Logger(request=request)


@router.post(settings.task_uri)
def task(
    logger: Logger = Depends(request_logger),
    state_change: StateChange = Depends(pubsub_state_change),
):
    """
    Initiate change state.
    """
    logger = logger.refine(state_change=state_change.dict())

    state_change.change_state(logger=logger)


@router.get(settings.scheduler_uri)
def schedule(
    logger: Logger = Depends(request_logger),
):
    """
    Checks if it's time to run a schedule.
    """
    Policy.check_all(logger)
