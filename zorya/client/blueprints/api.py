"""api.py"""
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

from zorya.util import tz
from zorya.model.policymodel import PolicyModel
from zorya.model.schedulesmodel import ScheduleModel

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
def add_schedule(schedule_model: ScheduleModel):
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
    schedule = ScheduleModel.get_by_name(schedule_name)

    return schedule.api_dict()


@router.get("/list_schedules")
def list_schedules():
    """
    Get all schedules.
    Returns: A list of schedules
    """
    schedule_ids = ScheduleModel.list_ids()

    return schedule_ids


@router.get("/del_schedule")
def del_schedule(schedule: str, response: Response):
    """
    Delete a schedule.
    """
    try:
        ScheduleModel.get_by_name(schedule).delete()
    except Exception as e:
        print(e)
        if "Forbidden" in str(e):
            response.status_code = 400
            return {"error": str(e)}

    return PlainTextResponse("ok")


@router.post("/add_policy")
def add_policy(policy: PolicyModel):
    """
    Add policy.
    """
    schedule = ScheduleModel.get_by_name(policy.schedulename)
    if not schedule.exists:
        return "schedule name not found", 404

    policy.set()

    return PlainTextResponse("ok")


@router.get("/get_policy")
def get_policy(policy: str):
    """
    Get policy.
    """
    policy = PolicyModel.get_by_name(policy)

    return policy.dict()


@router.get("/list_policies")
def list_policies():
    """
    Get all polices.
    Returns: List of policies
    """
    policy_ids = PolicyModel.list_ids()

    return policy_ids


@router.get("/del_policy")
def del_policy(policy: str):
    """
    Delete a policy
    """
    PolicyModel.get_by_name(policy).delete()

    return PlainTextResponse("ok")
