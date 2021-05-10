"""api.py"""
import json

from flask import Blueprint, request

from zorya.util import tz
from zorya.model.policymodel import PolicyModel
from zorya.model.schedulesmodel import ScheduleModel

API_VERSION = "/api/v1"


api = Blueprint(
    "api",
    __name__,
    url_prefix=API_VERSION,
)


@api.route("/time_zones", methods=["GET"])
def time_zones():
    """
    Get all time zones.
    :return: all time zone in the world wide world.
    """
    return json.dumps({"Timezones": tz.get_all_timezones()})


@api.route("/add_schedule", methods=["POST"])
def add_schedule():
    """
    Add a schedule.
    """
    ScheduleModel(**dict(request.json)).set()

    return "ok", 200


@api.route("/get_schedule", methods=["GET"])
def get_schedule():
    """
    Get a schedule.
    Returns: schedule json
    """
    schedule = ScheduleModel.get_by_name(request.args.get("schedule"))

    return json.dumps(schedule.api_dict())


@api.route("/list_schedules", methods=["GET"])
def list_schedules():
    """
    Get all schedules.
    Returns: A list of schedules
    """
    schedule_ids = ScheduleModel.list_ids()

    return json.dumps(schedule_ids)


@api.route("/del_schedule", methods=["GET"])
def del_schedule():
    """
    Delete a schedule.
    """
    name = request.args.get("schedule")
    ScheduleModel.get_by_name(name).delete()
    return "ok", 200


@api.route("/add_policy", methods=["POST"])
def add_policy():
    """
    Add policy.
    """
    schedule = ScheduleModel(request.json["schedulename"])
    if not schedule.exists:
        return "schedule name not found", 404

    PolicyModel(**request.json).set()

    return "ok", 200


@api.route("/get_policy", methods=["GET"])
def get_policy():
    """
    Get policy.
    """
    policy = PolicyModel.get_by_name(request.args.get("policy"))

    return json.dumps(policy.dict())


@api.route("/list_policies", methods=["GET"])
def list_policies():
    """
    Get all polices.
    Returns: List of policies
    """
    policy_ids = PolicyModel.list_ids()

    return json.dumps(policy_ids)


@api.route("/del_policy", methods=["GET"])
def del_policy():
    """
    Delete a policy
    """
    PolicyModel.get_by_name(request.args.get("policy")).delete()

    return "ok", 200
