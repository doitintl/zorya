"""Model for policy."""
import pydantic
from zorya.model.mixins import FireStoreMixin


class NodePoolModel(pydantic.BaseModel, FireStoreMixin):
    name: str
    num_nodes: int = 0

    @staticmethod
    def document_type():
        return "noodPooles"
