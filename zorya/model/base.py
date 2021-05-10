"""Model for policy."""
import os
from google.cloud import firestore

db = firestore.Client(project=os.environ["ZORYA_PROJECT"])


class BaseModel:
    DOCUMENT_TYPE = "BASE"
    name: str

    @property
    def ref(self):
        if not self._ref:
            self._ref = self.collection().document(self.name)
        return self._ref

    @property
    def exists(self):
        if not self._snap:
            self._snap = self.ref.get()
        return self._snap.exists

    @classmethod
    def collection(cls):
        return db.collection(f"zorya/v1/{cls.DOCUMENT_TYPE}")

    @classmethod
    def get_by_name(cls, name):
        schedule_ref = cls.collection().document(name)

        schedule_raw = schedule_ref.snap.to_dict()
        return cls(**schedule_raw)

    @classmethod
    def list_ids(cls):
        refs = cls.collection().stream()
        return [ref.id for ref in refs]

    @classmethod
    def delete(cls, name):
        cls(name).ref.delete()

    def set(self):
        self.ref.set(self.dict())
