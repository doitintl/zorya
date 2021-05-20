"""Model for policy."""
import json
from typing import List, Any, Dict, ClassVar

import pydantic
import google.auth
from google.cloud import pubsub

from zorya.models.firestore_base import FireStoreBase
from zorya.models.schedule import Schedule
from zorya.exceptions import DocumentNotFound
from zorya.logging import Logger
from zorya.settings import settings


class Policy(FireStoreBase):
    document_type: ClassVar[str] = "policies"

    name: str
    tags: List[Dict[str, str]] = pydantic.Field(default_factory=lambda: [])
    projects: List[Any] = pydantic.Field(default_factory=lambda: [])
    schedulename: str

    @classmethod
    def check_all(cls, logger: Logger):
        for policy in cls.list():
            try:
                policy.check_one(logger.refine(policy=policy.dict()))
            except DocumentNotFound:
                logger(
                    f"schedule {policy.schedulename} for policy {policy.name} not found!"
                )

    def check_one(self, logger: Logger):
        logger(f"checking policy {self.name!r}")

        schedule = Schedule.get_by_name(self.schedulename)
        logger = logger.refine(schedule=schedule.dict())

        if not schedule.changed:
            logger("conditions are met, nothing to do")
            return

        logger(f"state is changing to {schedule.desired_state}")

        credentials, _ = google.auth.default()

        publisher = pubsub.PublisherClient(credentials=credentials)
        topic_name = (
            f"projects/{settings.project_id}/topics/{settings.topic_id}"
        )

        futures = []

        for tagkeyvalue in self.tags:
            tagkey, tagvalue = next(iter(tagkeyvalue.items()))

            for project in self.projects:
                payload = {
                    "project": project,
                    "tagkey": tagkey,
                    "tagvalue": tagvalue,
                    "action": schedule.desired_state,
                }

                logger("inserting task", payload=payload)

                future = publisher.publish(
                    topic_name,
                    data=json.dumps(payload).encode("utf-8"),
                )

                futures.append(future)

        for future in futures:
            future.result()
