"""api.py"""
import pytz
from fastapi import APIRouter, Response, Query
from fastapi.responses import PlainTextResponse

from zorya.model.policy import Policy
from zorya.model.schedule import Schedule
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
    schedule = Schedule.get_by_name(schedule_name)

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
        Schedule.get_by_name(schedule_name).delete()
    except Exception as e:
        if "Forbidden" in str(e):
            response.status_code = 400
            return {"error": str(e)}

    return PlainTextResponse("ok")


@router.post("/add_policy")
def add_policy(policy: Policy):
    """
    Add policy.
    """
    schedule = Schedule.get_by_name(policy.schedulename)
    if not schedule.exists:
        return "schedule name not found", 404

    policy.set()

    return PlainTextResponse("ok")


@router.get("/get_policy")
def get_policy(
    policy_name: str = Query(..., alias="policy"),
):
    """
    Get policy.
    """
    policy = Policy.get_by_name(policy_name)

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
    Policy.get_by_name(policy_name).delete()

    return PlainTextResponse("ok")
