"""Model for policy."""
from zorya.model.base import BaseModel


class NodePoolModel(BaseModel):
    @staticmethod
    def document_type():
        return "noodPooles"

    name: str
    num_nodes: int = 0
