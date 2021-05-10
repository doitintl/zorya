"""Model for policy."""
from zorya.model.base import BaseModel


class NodePoolModel(BaseModel):
    DOCUMENT_TYPE = "noodPooles"

    name: str
    num_nodes: int = 0
