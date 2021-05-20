"""Database representation of schedule."""
import json
import enum
from datetime import datetime
from typing import ClassVar, Any, Tuple

import pytz
import pydantic
import numpy as np

from zorya.models.firestore_base import FireStoreBase

MATRIX_SIZE = 7 * 24


class Schedule(FireStoreBase):
    document_type: ClassVar[str] = "schedules"

    name: str
    timezone: str = pydantic.Field(
        default="UTC",
        choices=enum.Enum("TimezonesEnum", pytz.all_timezones),
    )
    ndarray: Any
    _now: int = 0

    @pydantic.validator("ndarray")
    def must_be_json_string(cls, v):
        if not v:
            v = np.zeros((7, 24)).tolist()
        if not isinstance(v, str):
            return json.dumps(v)
        return v

    def api_dict(self):
        data = self.dict()
        data["ndarray"] = json.loads(data["ndarray"])
        return data

    def delete(self):
        self.ref.delete()

    def parse_ndarray(self):
        return np.asarray(
            json.loads(self.ndarray),
            dtype=np.intc,
        ).flatten()

    @property
    def desired_state(self):
        return self._now

    @property
    def changed(self):
        arr = self.parse_ndarray()
        # if arr.shape != (1, 168):
        #     return False

        day, hour = local_day_hour(self.timezone)
        prev_index = get_prev_idx(day * 24 + hour, MATRIX_SIZE)
        prev = arr[prev_index]

        if self._now is None:
            self._now = arr[day * 24 + hour]

        return self._now != prev


def local_day_hour(timezone) -> Tuple[int, int]:
    now = datetime.now(tz=pytz.timezone(timezone))

    days = np.arange(0, 7)
    days = np.roll(days, 1)

    for index, item in enumerate(days):
        if item == now.weekday():
            return index, now.hour

    return (0, 0)


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
