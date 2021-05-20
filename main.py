"""Entry point to Zoyra."""
import logging
import json

from google.cloud import ndb
from flask import Flask, request
from model.policymodel import PolicyModel
from model.schedulesmodel import SchedulesModel
from tasks import policy_tasks, schedule_tasks
from util import tz

import google.cloud.logging

log_client = google.cloud.logging.Client()
log_client.setup_logging()


API_VERSION = "/api/v1"
app = Flask(__name__)
client = ndb.Client()


@app.route("/tasks/change_state", methods=["POST"])
def change_state():
    """
    Initiate change state.
    Returns:

    """
    payload = json.loads(request.get_data(as_text=False) or "(empty payload)")
    logging.debug(
        "Starting change_state action %s project %s tagkey %s tagvalue %s",
        payload["action"],
        payload["project"],
        payload["tagkey"],
        payload["tagvalue"],
    )
    schedule_tasks.change_state(
        payload["tagkey"], payload["tagvalue"], payload["action"], payload["project"]
    )
    return "ok", 200


@app.route("/tasks/schedule", methods=["GET"])
def schedule():
    """
    Checks if it's time to run a schedule.
    Returns:

    """
    logging.debug("From Cron start /tasks/schedule")

    with client.context():
        keys = PolicyModel.query().fetch(keys_only=True)
        for key in keys:
            logging.debug("Creating deferred task for   %s", key.id())
            policy_tasks.policy_checker(key.id())
    return "ok", 200


@app.route(API_VERSION + "/time_zones", methods=["GET"])
def time_zones():
    """
    Get all time zones.
    :return: all time zone in the world wide world.
    """
    return json.dumps({"Timezones": tz.get_all_timezones()})


@app.route(API_VERSION + "/add_schedule", methods=["POST"])
def add_schedule():
    """
    Add a schedule.
    Returns:

    """
    with client.context():
        schedules_model = SchedulesModel()
        schedules_model.Schedule = {
            "dtype": request.json["dtype"],
            "Corder": request.json["Corder"],
            "Shape": request.json["Shape"],
            "__ndarray__": request.json["__ndarray__"],
        }

        schedules_model.Name = request.json["name"]
        schedules_model.DisplayName = request.json.get(
            "displayname", request.json.get("name"))
        schedules_model.Timezone = request.json["timezone"]
        schedules_model.key = ndb.Key("SchedulesModel", request.json["name"])
        schedules_model.put()
    return "ok", 200


@app.route(API_VERSION + "/get_schedule", methods=["GET"])
def get_schedule():
    """
    Get a schedule.
    Returns: schedule json

    """
    name = request.args.get("schedule")
    schedule = {}
    with client.context():
        res = SchedulesModel.query(SchedulesModel.Name == name).get()
        if not res:
            return "not found", 404
        schedule.update({"name": res.Name})
        schedule.update({"displayname": res.DisplayName or res.Name})
        schedule.update(res.Schedule)
        schedule.update({"timezone": res.Timezone})
        logging.debug(json.dumps(res.Schedule))
    return json.dumps(schedule)


@app.route(API_VERSION + "/list_schedules", methods=["GET"])
def list_schedules():
    """
    Get all schedules.
    Returns: A list of schedules

    """
    schedules_list = []
    with client.context():
        verbose = request.args.get("verbose") == "true"
            schedules = SchedulesModel.query().fetch()
            for schedule in schedules:
                schedules_list.append(
                    {"name": schedule.Name, "displayName": schedule.DisplayName}
                )
        else:
            keys = SchedulesModel.query().fetch(keys_only=True)
            for key in keys:
                schedules_list.append(key.id())
    return json.dumps(schedules_list)


@app.route(API_VERSION + "/del_schedule", methods=["GET"])
def del_schedule():
    """
    Delete a schedule.
    Returns:

    """
    name = request.args.get("schedule")
    with client.context():
        res = SchedulesModel.query(SchedulesModel.Name == name).get()
        if not res:
            return "not found", 404
        policy = PolicyModel.query(PolicyModel.Schedule == name).get()
        if policy:
            return "Forbidden policy {} is using the schedule".format(policy.Name), 403
        res.key.delete()
    return "ok", 200


@app.route(API_VERSION + "/add_policy", methods=["POST"])
def add_policy():
    """
    Add policy.
    Returns:

    """
    logging.debug(json.dumps(request.json))
    name = request.json["name"]
    display_name = request.json.get("displayname", name)
    tags = request.json["tags"]
    projects = request.json["projects"]
    schedule_name = request.json["schedulename"]
    with client.context():
        res = SchedulesModel.query(SchedulesModel.Name == schedule_name).get()
        if not res:
            return "not found", 404

        policy_model = PolicyModel()
        policy_model.Name = name
        policy_model.DisplayName = display_name
        policy_model.Tags = tags
        policy_model.Projects = projects
        policy_model.Schedule = schedule_name
        policy_model.key = ndb.Key("PolicyModel", name)
        policy_model.put()
    return "ok", 200


@app.route(API_VERSION + "/get_policy", methods=["GET"])
def get_policy():
    """
    Get policy.
    Returns: policy json

    """
    policy = {}
    name = request.args.get("policy")
    with client.context():
        res = PolicyModel.query(PolicyModel.Name == name).get()
        logging.debug(res)
        if not res:
            return "not found", 404
        policy.update({"name": res.Name})
        policy.update({"displayname": res.DisplayName or res.Name})
        policy.update({"schedulename": res.Schedule})
        policy.update({"tags": res.Tags})
        policy.update({"projects": res.Projects})
    return json.dumps(policy)


@app.route(API_VERSION + "/list_policies", methods=["GET"])
def list_policies():
    """
    Get all polices.
    Returns: List of policies

    """
    policies_list = []
    with client.context():
        verbose = request.args.get("verbose") == "true"
            policies = PolicyModel.query().fetch()
            for policy in policies:
                policies_list.append(
                    {"name": policy.Name, "displayName": policy.DisplayName}
                )
        else:
            keys = PolicyModel.query().fetch(keys_only=True)
            for key in keys:
                policies_list.append(key.id())

    return json.dumps(policies_list)


@app.route(API_VERSION + "/del_policy", methods=["GET"])
def del_policy():
    """
    Delete a policy
    Returns:

    """
    name = request.args.get("policy")
    with client.context():
        res = PolicyModel.query(PolicyModel.Name == name).get()
        if not res:
            return "not found", 404
        res.key.delete()
    return "ok", 200


@app.route("/")
def index():
    """
    Main Page
    :return:
    """
    return "ok", 200


if __name__ == "__main__":
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.INFO)
    app.run(debug=False)
