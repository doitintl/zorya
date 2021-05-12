"""pubsub.py"""
import json
import base64
from datetime import datetime

import pydantic


class PubSubMessage(pydantic.BaseModel):
    messageId: str
    data: str
    publish_time: datetime
    message_id: str

    @property
    def payload_json(self):
        json_str = base64.b64decode(self.data).decode("utf-8").strip()
        return json.loads(json_str)


class PubSubEnvelope(pydantic.BaseModel):
    message: PubSubMessage
    subscription: str
