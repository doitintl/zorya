"""Time zone utilities."""
from datetime import datetime, timedelta

import numpy as np
import pytz
import tzlocal


def get_all_timezones():
    """Get a list of all timezones."""
    return pytz.all_timezones


def get_local_timezone():
    """
    Get the local timezone.
    Returns: local time zone.

    """
    return tzlocal.get_localzone()


def get_time_at_timezone(timezone):
    """
    Get the current time a a time zone.
    Args:
        timezone:

    Returns: time at the requestd timezone

    """
    tz = pytz.timezone(timezone)
    now = datetime.now(tz=tz)
    target_tz = pytz.timezone(timezone)
    return target_tz.normalize(now.astimezone(target_tz))


def convert_time_to_index(time):
    """
    Convert a time to and index in an 7x24 array.
    Args:
        time:

    Returns: x,y of the index

    """
    days = np.arange(0, 7)
    days = np.roll(days, 1)
    for index, item in enumerate(days):
        if item == time.weekday():
            day = index
    hour = time.hour
    return day, hour

def get_next_hour():
    n = datetime.now() + timedelta(hours=1)
    new_date = datetime(year=n.year, month=n.month, day=n.day, hour=n.hour)
    return new_date

