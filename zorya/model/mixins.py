"""Model for policy."""
import os

from google.cloud import firestore

db = firestore.Client(project=os.environ["ZORYA_PROJECT"])


class FireStoreMixin:
    @staticmethod
    def document_type():
        return "BASE"

    @property
    def document_id(self):
        return self.name

    @property
    def ref(self):
        return self.collection().document(self.document_id)

    @property
    def exists(self):
        return self.ref.get().exists

    @classmethod
    def collection(cls):
        return db.collection(f"zorya/v1/{cls.document_type()}")

    @classmethod
    def get_by_name(cls, name):
        ref = cls.collection().document(name)
        snap = ref.get()

        instance = cls(**snap.to_dict())
        return instance

    @classmethod
    def list_ids(cls):
        refs = cls.collection().stream()
        return [ref.id for ref in refs]

    @classmethod
    def list(cls):
        refs = cls.collection().stream()
        for ref in refs:
            snap = ref.get()
            policy = cls(**snap.to_dict())
            yield policy

    def delete(self):
        self.ref.delete()

    def set(self):
        self.ref.set(self.dict())
