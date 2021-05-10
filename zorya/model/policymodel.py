"""Model for policy."""
import os
from typing import List, Any, Dict

import pydantic
from google.cloud import firestore

from zorya.model.base import BaseModel


db = firestore.Client(project=os.environ["ZORYA_PROJECT"])


class PolicyModel(pydantic.BaseModel, BaseModel):
    DOCUMENT_TYPE = "policies"

    name: str
    tags: List[Dict[str, str]] = None
    projects: List[Any] = None
    schedulename: str
