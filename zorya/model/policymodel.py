"""Model for policy."""
from typing import List, Any, Dict
from pydantic import BaseModel


class PolicyModel(BaseModel):
    """Class that represents a tags and their associated schedule."""

    name: str
    tags: List[Dict[str, str]] = None
    projects: List[Any] = None
    schedulename: str
