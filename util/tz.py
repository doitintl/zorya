"""Time zone utilities."""
from datetime import datetime

import tzlocal
import pytz
import numpy as np


def get_all_timezones():
    """Get a list of all timezones."""
    return pytz.all_timezones


def get_local_timezone():
    return tzlocal.get_localzone()


def get_time_at_timezone(timezone):
    tz = pytz.timezone(timezone)
    now = datetime.now(tz=tz)
    target_tz = pytz.timezone(timezone)
    return  target_tz.normalize(now.astimezone(target_tz))


def convert_time_to_index(time):
    days = np.arange(0,7)
    days = np.roll(days, 1)
    for index, item in enumerate(days):
        if item == time.weekday():
            day = index
    hour = time.hour
    return day, hour




