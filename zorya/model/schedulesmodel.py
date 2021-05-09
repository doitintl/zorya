"""Database representation of schedule."""
import json
import enum
from typing import Any

from pydantic import BaseModel, Field, validator

from zorya.util import tz


class ScheduleModel(BaseModel):
    name: str
    timezone: str = Field(
        default="UTC",
        choices=enum.Enum("TimezonesEnum", tz.get_all_timezones()),
    )
    ndarray: Any

    @validator("ndarray")
    def must_be_json_string(cls, v):
        if not isinstance(v, str):
            return json.dumps(v)
        return v

    def api_dict(self):
        data = self.dict()
        data["ndarray"] = json.loads(data["ndarray"])
        return data
