"""api.py"""
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

from zorya.util import tz
from zorya.model.policy import Policy
from zorya.model.schedule import Schedule

API_VERSION = "/api/v1"


router = APIRouter(
    prefix=API_VERSION,
    responses={404: {"description": "Not found"}},
)


@router.get("/time_zones")
def time_zones():
    """
    Get all time zones.
    :return: all time zone in the world wide world.
    """
    return {"Timezones": tz.get_all_timezones()}


@router.post("/add_schedule")
def add_schedule(schedule_model: Schedule):
    """
    Add a schedule.
    """
    schedule_model.set()

    return PlainTextResponse("ok")


@router.get("/get_schedule")
def get_schedule(schedule_name: str):
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
def del_schedule(schedule: str, response: Response):
    """
    Delete a schedule.
    """
    try:
        Schedule.get_by_name(schedule).delete()
    except Exception as e:
        print(e)
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
def get_policy(policy: str):
    """
    Get policy.
    """
    policy = Policy.get_by_name(policy)

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
def del_policy(policy: str):
    """
    Delete a policy
    """
    Policy.get_by_name(policy).delete()

    return PlainTextResponse("ok")
