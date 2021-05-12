"""Model for policy."""
from typing import List, Any, Dict, ClassVar

import pydantic

from zorya.model.mixins import FireStoreMixin


class Policy(pydantic.BaseModel, FireStoreMixin):
    document_type: ClassVar[str] = "policies"

    name: str
    tags: List[Dict[str, str]] = None
    projects: List[Any] = None
    schedulename: str
