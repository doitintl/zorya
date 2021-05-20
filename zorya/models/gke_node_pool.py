"""Model for policy."""
from typing import ClassVar, List

from zorya.models.firestore_base import FireStoreBase


class GKENodePool(FireStoreBase):
    document_type: ClassVar[str] = "noodPooles"

    name: str
    num_nodes: int = 0
    instanceGroupUrls: List[str]

    @classmethod
    def get_by_url(cls, url):
        name = url.split("/")[-1]
        return cls.get_by_name(name)
