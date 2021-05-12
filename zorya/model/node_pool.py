"""Model for policy."""
from typing import ClassVar

import pydantic
from zorya.model.mixins import FireStoreMixin


class NodePoolModel(pydantic.BaseModel, FireStoreMixin):
    document_type: ClassVar[str] = "noodPooles"

    name: str
    num_nodes: int = 0

    @classmethod
    def get_by_url(cls, url):
        name = url.split("/")[-1]
        return cls.get_by_name(name)
