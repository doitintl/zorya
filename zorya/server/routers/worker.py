"""Zoyra Worker"""
from fastapi import APIRouter, Request, Depends

from zorya.model.state_change import StateChange
from zorya.model.pubsub import PubSubEnvelope
from zorya.tasks import policy_tasks, schedule_tasks
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

    schedule_tasks.change_state(state_change, logger=logger)


@router.get(settings.scheduler_uri)
def schedule(request: Request):
    """
    Checks if it's time to run a schedule.
    """
    policy_tasks.check_all(request)
