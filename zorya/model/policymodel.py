"""Model for policy."""
from typing import List, Any, Dict

import pydantic

from zorya.model.mixins import FireStoreMixin


class PolicyModel(pydantic.BaseModel, FireStoreMixin):
    name: str
    tags: List[Dict[str, str]] = None
    projects: List[Any] = None
    schedulename: str

    @staticmethod
    def document_type():
        return "policies"
