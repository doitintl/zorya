"""api.py"""
import pytz
from starlette.responses import JSONResponse
from zorya.exceptions import DocumentNotFound
from fastapi import APIRouter, Response, Query
from fastapi.responses import PlainTextResponse

from zorya.models.policy import Policy
from zorya.models.schedule import Schedule
from zorya.server.logged_route import LoggedRoute

API_VERSION = "/api/v1"


router = APIRouter(prefix=API_VERSION, route_class=LoggedRoute)


@router.get("/time_zones")
def time_zones():
    """
    Get all time zones.
    :return: all time zone in the world wide world.
    """
    return {"Timezones": pytz.all_timezones}


@router.post("/add_schedule")
def add_schedule(schedule_model: Schedule):
    """
    Add a schedule.
    """
    schedule_model.set()

    return PlainTextResponse("ok")


@router.get("/get_schedule")
def get_schedule(schedule_name: str = Query(..., alias="schedule")):
    """
    Get a schedule.
    Returns: schedule json
    """
    try:
        schedule = Schedule.get_by_name(schedule_name)
    except DocumentNotFound:
        return JSONResponse({"details": "schedule not found"}, status_code=404)

    return schedule.api_dict()


@router.get("/list_schedules")
def list_schedules():
    """
    Get all schedules.
    Returns: A list of schedules
    """
    schedule_ids = Schedule.list_ids()

    return schedule_ids


@router.get("/del_schedule")
def del_schedule(
    response: Response,
    schedule_name: str = Query(..., alias="schedule"),
):
    """
    Delete a schedule.
    """
    try:
        schedule = Schedule.get_by_name(schedule_name)
    except DocumentNotFound:
        return JSONResponse({"details": "schedule not found"}, status_code=404)

    used_by_policies = (
        Policy.collection().where("schedulename", "==", schedule.name).stream()
    )

    for policy in used_by_policies:
        return JSONResponse(
            {
                "details": f"Forbidden policy {policy.id!r} is using the schedule"
            },
            status_code=400,
        )

    schedule.delete()
    return PlainTextResponse("ok")


@router.post("/add_policy")
def add_policy(policy: Policy):
    """
    Add policy.
    """
    try:
        Schedule.get_by_name(policy.schedulename)
    except DocumentNotFound:
        return JSONResponse({"details": "schedule not found"}, status_code=404)

    policy.set()

    return PlainTextResponse("ok")


@router.get("/get_policy")
def get_policy(
    policy_name: str = Query(..., alias="policy"),
):
    """
    Get policy.
    """
    try:
        policy = Policy.get_by_name(policy_name)
    except DocumentNotFound:
        return JSONResponse({"details": "policy not found"}, status_code=404)

    return policy.dict()


@router.get("/list_policies")
def list_policies():
    """
    Get all polices.
    Returns: List of policies
    """
    policy_ids = Policy.list_ids()

    return policy_ids


@router.get("/del_policy")
def del_policy(policy_name: str = Query(..., alias="policy")):
    """
    Delete a policy
    """
    try:
        policy = Policy.get_by_name(policy_name)
    except DocumentNotFound:
        return JSONResponse({"details": "policy not found"}, status_code=404)

    policy.delete()

    return PlainTextResponse("ok")
