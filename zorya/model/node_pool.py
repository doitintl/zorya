"""Model for policy."""
from typing import ClassVar

import pydantic
from zorya.model.mixins import FireStoreMixin


class NodePoolModel(pydantic.BaseModel, FireStoreMixin):
    document_type: ClassVar[str] = "noodPooles"

    name: str
    num_nodes: int = 0
