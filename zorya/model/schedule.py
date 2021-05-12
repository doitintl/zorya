"""Database representation of schedule."""
import json
import enum
from typing import ClassVar, Any

import pydantic
import numpy as np

from zorya.model.mixins import FireStoreMixin
from zorya.model.policy import Policy
from zorya.util import tz, utils

MATRIX_SIZE = 7 * 24


class Schedule(pydantic.BaseModel, FireStoreMixin):
    document_type: ClassVar[str] = "schedules"

    name: str
    timezone: str = pydantic.Field(
        default="UTC",
        choices=enum.Enum("TimezonesEnum", tz.get_all_timezones()),
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
        local_time = tz.get_time_at_timezone(self.timezone)
        day, hour = tz.convert_time_to_index(local_time)
        prev_index = utils.get_prev_idx(day * 24 + hour, MATRIX_SIZE)
        prev = arr[prev_index]

        if self._now is None:
            self._now = arr[day * 24 + hour]

        return self._now == prev
