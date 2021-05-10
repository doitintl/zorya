"""Database representation of schedule."""
import os
import json
import enum
from typing import Any

import pydantic
from google.cloud import firestore

from zorya.model.base import BaseModel
from zorya.model.policymodel import PolicyModel
from zorya.util import tz

db = firestore.Client(project=os.environ["ZORYA_PROJECT"])


class ScheduleModel(pydantic.BaseModel, BaseModel):
    DOCUMENT_TYPE = "schedules"

    name: str
    timezone: str = pydantic.Field(
        default="UTC",
        choices=enum.Enum("TimezonesEnum", tz.get_all_timezones()),
    )
    ndarray: Any

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
                f"Forbidden policy {policy.id} is using the schedule"
            )
        self.ref.delete()

    def used_by(self):
        return (
            PolicyModel.collection()
            .where("schedulename", "==", self.name)
            .stream()
        )
