import pytest
from typing import Callable, Dict
from types import GeneratorType

from zorya.models.firestore_base import FireStoreBase
from zorya.exceptions import DocumentNotFound


class DummyChild(FireStoreBase):
    name: str

    def document_type(self) -> str:
        return "DUMMY"


def test_firestore_exists():
    name = "name"

    assert DummyChild(name=name).exists is False

    DummyChild(name=name).set()
    assert DummyChild(name=name).exists is True


def test_firestore_set_get_by_name(
    assert_dict_equal: Callable[[Dict, Dict], bool],
):
    name = "dummy-name"
    with pytest.raises(DocumentNotFound):
        DummyChild.get_by_name(name)

    dummy_child = DummyChild(name=name)
    dummy_child.set()

    fetched_dummy_child = DummyChild.get_by_name(name)

    assert_dict_equal(fetched_dummy_child.dict(), dummy_child.dict())


def test_firestore_list():
    names = ["name1", "name2", "name3"]
    for name in names:
        DummyChild(name=name).set()

    assert isinstance(DummyChild.list(), GeneratorType)

    count = 0
    names_set = set(names)
    for child in DummyChild.list():
        assert isinstance(child, DummyChild)
        assert child.name in names

        names_set = names_set - set([child.name])
        count += 1

    assert count == len(names)
    assert not names_set


def test_firestore_list_ids():
    names = ["name1", "name2", "name3"]
    for name in names:
        DummyChild(name=name).set()

    assert isinstance(DummyChild.list_ids(), list)

    assert DummyChild.list_ids() == names
