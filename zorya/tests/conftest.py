"""conftest.py"""
import os
import signal
import psutil
import subprocess
from unittest import TestCase

import numpy as np
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import pytest
from google.cloud import firestore
from google.auth.credentials import AnonymousCredentials

from zorya.models import firestore_base

HOST = "localhost"
PORT = "8080"
MOCK_PROJECT = "your-project-id"

os.environ["FIRESTORE_EMULATOR_HOST"] = f"{HOST}:{PORT}"
os.environ["GCLOUD_PROJECT"] = MOCK_PROJECT


@pytest.fixture(scope="session", autouse=True)
def db_client():
    print("starting firestore emulator")

    process = subprocess.Popen(
        f"gcloud beta emulators firestore start --host-port={HOST}:{PORT}".split(),
        shell=False,
    )

    firestore_base.db = firestore.Client(
        credentials=AnonymousCredentials(), project=MOCK_PROJECT
    )

    yield

    print("killing firestore emulator")

    parent = psutil.Process(process.pid)
    children = parent.children(recursive=True)
    children.append(parent)
    for p in children:
        try:
            p.send_signal(signal.SIGTERM)
        except psutil.NoSuchProcess:
            pass
    psutil.wait_procs(children, timeout=5)


@pytest.fixture(autouse=True)
def clear_db():
    url = (
        f"http://{HOST}:{PORT}/emulator/v1/projects/{MOCK_PROJECT}"
        "/databases/(default)/documents"
    )
    s = requests.Session()

    retries = Retry(total=5, backoff_factor=0.1)

    s.mount("http://", HTTPAdapter(max_retries=retries))

    s.delete(url)
    print("cleared firestore emulator")


@pytest.fixture(autouse=True)
def anonymous_adc(monkeypatch: pytest.MonkeyPatch):
    def _anonymous_adc():
        return AnonymousCredentials(), MOCK_PROJECT

    monkeypatch.setattr("google.auth.default", _anonymous_adc)


@pytest.fixture
def empty_schedule_array():
    return np.zeros((7, 24)).tolist()


@pytest.fixture
def dummy_schedule_raw(empty_schedule_array):
    return {
        "name": "test-schedule",
        "timezone": "UTC",
        "ndarray": empty_schedule_array,
    }


@pytest.fixture
def dummy_policy_raw():
    return {
        "name": "test-policy",
        "schedulename": "test-schedule",
        "tags": [
            {"test-tagkey1": "test-tagvalue1"},
            {"test-tagkey2": "test-tagvalue2"},
            {"test-tagkey3": "test-tagvalue3"},
        ],
        "projects": ["test-project1", "test-project2"],
    }


@pytest.fixture
def state_change_raw():
    return {
        "tagkey": "tagkey",
        "tagvalue": "tagvalue",
        "action": 1,
        "project": "project",
    }


@pytest.fixture
def assert_dict_equal():
    return TestCase().assertDictEqual
