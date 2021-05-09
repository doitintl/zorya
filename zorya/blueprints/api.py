"""api.py"""
import os
import json

from flask import Blueprint, request
from google.cloud import firestore

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
    schedule = ScheduleModel(**dict(request.json))

    db = firestore.Client(os.environ["ZORYA_PROJECT"])
    schedule_ref = db.collection("zorya/v1/schedules").document(schedule.name)
    schedule_ref.set(schedule.dict())

    return "ok", 200


@api.route("/get_schedule", methods=["GET"])
def get_schedule():
    """
    Get a schedule.
    Returns: schedule json
    """
    db = firestore.Client(os.environ["ZORYA_PROJECT"])
    schedule_ref = db.collection("zorya/v1/schedules").document(
        request.args.get("schedule"),
    )
    schedule_raw = schedule_ref.get().to_dict()
    schedule = ScheduleModel(**schedule_raw)

    return json.dumps(schedule.api_dict())


@api.route("/list_schedules", methods=["GET"])
def list_schedules():
    """
    Get all schedules.
    Returns: A list of schedules
    """
    db = firestore.Client(os.environ["ZORYA_PROJECT"])
    schedule_refs = db.collection("zorya/v1/schedules").stream()
    schedules = []
    for schedule_ref in schedule_refs:
        schedules.append(schedule_ref.id)

    return json.dumps(schedules)


@api.route("/del_schedule", methods=["GET"])
def del_schedule():
    """
    Delete a schedule.
    """
    db = firestore.Client(os.environ["ZORYA_PROJECT"])
    schedule_name = request.args.get("schedule")
    schedule_ref = db.collection("zorya/v1/schedules").document(schedule_name)
    if not schedule_ref.get().exists:
        return "not found", 404

    used_by = (
        db.collection("zorya/v1/policies")
        .where("schedulename", "==", schedule_name)
        .stream()
    )

    for policy in used_by:
        return (
            "Forbidden policy {} is using the schedule".format(policy.id),
            403,
        )
    schedule_ref.delete()
    return "ok", 200


@api.route("/add_policy", methods=["POST"])
def add_policy():
    """
    Add policy.
    """
    db = firestore.Client(os.environ["ZORYA_PROJECT"])
    schedule_ref = db.collection("zorya/v1/schedules").document(
        request.json["schedulename"]
    )
    if not schedule_ref.get().exists:
        return "schedule name not found", 404

    policy = PolicyModel(**request.json)

    policy_ref = db.collection("zorya/v1/policies").document(policy.name)
    policy_ref.set(policy.dict())

    return "ok", 200


@api.route("/get_policy", methods=["GET"])
def get_policy():
    """
    Get policy.
    """
    db = firestore.Client(os.environ["ZORYA_PROJECT"])
    policy_ref = db.collection("zorya/v1/policies").document(
        request.args.get("policy")
    )
    policy = PolicyModel(**policy_ref.get().to_dict())

    return json.dumps(policy.dict())


@api.route("/list_policies", methods=["GET"])
def list_policies():
    """
    Get all polices.
    Returns: List of policies
    """
    db = firestore.Client(os.environ["ZORYA_PROJECT"])
    policy_refs = db.collection("zorya/v1/policies").stream()
    policies = []
    for policy_ref in policy_refs:
        policies.append(policy_ref.id)
    return json.dumps(policies)


@api.route("/del_policy", methods=["GET"])
def del_policy():
    """
    Delete a policy
    """
    db = firestore.Client(os.environ["ZORYA_PROJECT"])
    policy_ref = db.collection("zorya/v1/policies").document(
        request.args.get("policy")
    )
    policy_ref.delete()

    return "ok", 200
