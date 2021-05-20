"""Model for policy."""
import abc
from typing import List

from google.cloud import firestore
import pydantic

from zorya.exceptions import DocumentNotFound
from zorya.settings import settings

db = firestore.Client(project=settings.project_id)


class FireStoreBase(pydantic.BaseModel):
    @property
    @abc.abstractmethod
    def document_type(self) -> str:
        pass

    @property
    def document_id(self) -> str:
        return self.name

    @property
    def ref(self):
        return self.collection().document(self.document_id)

    @property
    def exists(self) -> bool:
        return self.ref.get().exists

    @classmethod
    def collection(cls):
        return db.collection(f"zorya/v1/{cls.document_type}")

    @classmethod
    def get_by_name(cls, name: str):
        ref = cls.collection().document(name)
        snap = ref.get()

        if not snap.exists:
            raise DocumentNotFound(ref.path)

        instance = cls(**snap.to_dict())
        return instance

    @classmethod
    def list_ids(cls) -> List[str]:
        refs = cls.collection().stream()
        return [ref.id for ref in refs]

    @classmethod
    def list(cls):
        refs = cls.collection().stream()
        for snap in refs:
            # snap = ref.get()
            policy = cls(**snap.to_dict())
            yield policy

    def delete(self) -> None:
        self.ref.delete()

    def set(self):
        self.ref.set(self.dict())
