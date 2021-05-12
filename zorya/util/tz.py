"""Time zone utilities."""
from datetime import datetime

import numpy as np
import pytz


def get_all_timezones():
    """Get a list of all timezones."""
    return pytz.all_timezones


def local_day_hour(timezone):
    """
    Get the current time a a time zone.
    Args:
        timezone:

    Returns: time at the requestd timezone

    """
    now = datetime.now(tz=pytz.timezone(timezone))

    days = np.arange(0, 7)
    days = np.roll(days, 1)

    for index, item in enumerate(days):
        if item == now.weekday():
            return index, now.hour
