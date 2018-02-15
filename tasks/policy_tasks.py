import logging

from google.appengine.api import taskqueue

import numpy as np
from model.policymodel import PolicyModel
from model.schedulesmodel import SchedulesModel
from util import tz, utils


def policy_checker(name):
    policy = PolicyModel.query(PolicyModel.Name == name).get()
    if not policy:
        logging.error('Policy %s not found!', name)
        return 'not found', 404
    schedule = SchedulesModel.query(
        SchedulesModel.Name == policy.Schedule).get()
    if not schedule:
        logging.error('Schedule %s not found!', policy.Schedule)
        return 'not found', 404
    day, hour = tz.convert_time_to_index(
        tz.get_time_at_timezone(schedule.Timezone))
    logging.debug("Working on %s %s", day, hour)
    arr = np.asarray(schedule.Schedule['__ndarray__'], dtype=np.int).flatten()
    matrix_size = schedule.Schedule['Shape'][0] * schedule.Schedule['Shape'][
        1]
    prev = utils.get_prev_idx(day * 24 + hour, matrix_size)
    now = arr[day * 24 + hour]
    prev = arr[prev]
    if now == prev:
        # do nothing
        logging.info("Nothing should be done for %s", name)
        return 'ok', 200
    else:
        # stop/start
        logging.info("State is changing for %s", name)
        # for each tag lets do it
        for tag in policy.Tags:
            for project in policy.Projects:
                task = taskqueue.add(queue_name='default',
                                     url="/tasks/change_state",
                                     method='GET',
                                     params={
                                         'project': project,
                                         'tagkey': tag.keys(),
                                         'tagvalue': tag.values(),
                                         'action': now
                                     })
                logging.debug('Task %s enqueued, ETA %s.', task.name,
                              task.eta)
        return 'ok', 200
