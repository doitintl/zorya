import logging

from google.appengine.ext import deferred, ndb

from flask import Flask, request
from model.policymodel import PolicyModel
from model.schedulesmodel import SchedulesModel
from tasks import policy_tasks, schedule_tasks
from util import tz

API_VERSION = '/api/v1'
app = Flask(__name__)
import json


@app.route('/tasks/change_state', methods=['GET'])
def change_state():
    logging.debug(
        "Starting change_state action %s project %s tagkey %s tagvalue %s",
        request.args['tagkey'], request.args['tagvalue'],
        request.args['action'], request.args['project'])
    schedule_tasks.change_state(
        request.args['tagkey'], request.args['tagvalue'],
        request.args['action'], request.args['project'])
    return 'ok', 200


@app.route(API_VERSION + '/time_zones', methods=['GET'])
def time_zones():
    """
    Get all time zones.
    :return: all time zone in the world wide world.
    """
    return json.dumps({'Timezones': tz.get_all_timezones()})


@app.route(API_VERSION + '/schedule')
def schedule():
    logging.debug("Start/tasks/schedule")
    keys = PolicyModel.query().fetch(keys_only=True)
    for key in keys:
        logging.debug("Key = %s", key.id())
        deferred.defer(policy_tasks.policy_checker, key.id())
    return 'ok', 200


@app.route(API_VERSION + '/add_schedule', methods=['POST'])
def add_schedule():
    schedules_model = SchedulesModel()
    schedules_model.Schedule = {
        'dtype': request.json['schedule']['dtype'],
        'Corder': request.json['schedule']['Corder'],
        'Shape': request.json['schedule']['shape'],
        '__ndarray__': request.json['schedule']['__ndarray__']
    }
    schedules_model.Name = request.json['name']
    schedules_model.Timezone = request.json['timezone']
    schedules_model.key = ndb.Key('SchedulesModel', request.json['name'])
    schedules_model.put()
    return 'ok', 200


@app.route(API_VERSION + '/get_schedule')
def get_schedule():
    name = request.args.get('schedule')
    res = SchedulesModel.query(SchedulesModel.Name == name).get()
    if not res:
        return 'not found', 404
    schedule = {}
    schedule.update({'name': res.Name})
    schedule.update(res.Schedule)
    schedule.update({'timezone': res.Timezone})
    print res.Schedule
    return json.dumps(schedule)


@app.route(API_VERSION + '/add_policy', methods=['POST'])
def add_policy():
    print(request.json)
    name = request.json['name']
    tags = request.json['tags']
    projects = request.json['projetcs']
    schedule_name = request.json['schedulename']

    res = SchedulesModel.query(SchedulesModel.Name == schedule_name).get()
    if not res:
        return 'not found', 404

    policy_model = PolicyModel()
    policy_model.Name = name
    policy_model.Tags = tags
    policy_model.Projects = projects
    policy_model.Schedule = schedule_name
    policy_model.key = ndb.Key('PolicyModel', name)
    policy_model.put()
    return 'ok', 200


@app.route(API_VERSION + '/get_policy')
def get_policy():
    name = request.args.get('policy')
    res = PolicyModel.query(PolicyModel.Name == name).get()
    print res
    if not res:
        return 'not found', 404
    policy = {}
    policy.update({'name': res.Name})
    policy.update({'schedule': res.Schedule})
    policy.update({'tags': res.Tags})
    policy.update({'projetcs': res.Projects})
    return json.dumps(policy)


@app.route('/')
def index():
    """
    Main Page
    :return:
    """
    return 'ok', 200


if __name__ == '__main__':
    app.run(debug=True)
