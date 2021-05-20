"""pubsub.py"""
import json
import base64
from datetime import datetime

import pydantic


class PubSubMessage(pydantic.BaseModel):
    message_id: str
    data: str
    publish_time: datetime

    @property
    def payload_json(self):
        json_str = base64.b64decode(self.data).decode("utf-8").strip()
        return json.loads(json_str)


class PubSubEnvelope(pydantic.BaseModel):
    message: PubSubMessage
    subscription: str
