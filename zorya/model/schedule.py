"""Database representation of schedule."""
import json
import enum
from datetime import datetime
from typing import ClassVar, Any

import pytz
import pydantic
import numpy as np

from zorya.model.policy import Policy
from zorya.model.mixins import FireStoreMixin

MATRIX_SIZE = 7 * 24


class Schedule(pydantic.BaseModel, FireStoreMixin):
    document_type: ClassVar[str] = "schedules"

    name: str
    timezone: str = pydantic.Field(
        default="UTC",
        choices=enum.Enum("TimezonesEnum", pytz.all_timezones),
    )
    ndarray: Any
    _now: int = None

    @pydantic.validator("ndarray")
    def must_be_json_string(cls, v):
        if not isinstance(v, str):
            return json.dumps(v)
        return v

    def api_dict(self):
        data = self.dict()
        data["ndarray"] = json.loads(data["ndarray"])
        return data

    def delete(self):
        for policy in self.used_by():
            raise Exception(
                f"Forbidden policy {policy.id!r} is using the schedule"
            )
        self.ref.delete()

    def used_by(self):
        return (
            Policy.collection().where("schedulename", "==", self.name).stream()
        )

    def parse_ndarray(self):
        return np.asarray(
            json.loads(self.ndarray),
            dtype=np.int,
        ).flatten()

    @property
    def desired_state(self):
        return self._now

    @property
    def changed(self):
        arr = self.parse_ndarray()
        day, hour = local_day_hour(self.timezone)
        prev_index = get_prev_idx(day * 24 + hour, MATRIX_SIZE)
        prev = arr[prev_index]

        if self._now is None:
            self._now = arr[day * 24 + hour]

        return self._now == prev


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


def get_prev_idx(idx, matrix_size):
    """
    Get the previous index in the matrix.
    Args:
        idx: current index
        matrix_size: matrix size

    Returns:

    """
    if idx == 0:
        return matrix_size - 1
    else:
        return idx - 1
