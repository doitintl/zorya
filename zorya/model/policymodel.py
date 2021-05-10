"""Model for policy."""
import os
from typing import List, Any, Dict

from google.cloud import firestore

from zorya.model.base import BaseModel


db = firestore.Client(project=os.environ["ZORYA_PROJECT"])


class PolicyModel(BaseModel):

    name: str
    tags: List[Dict[str, str]] = None
    projects: List[Any] = None
    schedulename: str

    @staticmethod
    def document_type():
        return "policies"
