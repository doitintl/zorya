from typing import List, Dict, Any, Callable

import pytz
import pytest
from fastapi.testclient import TestClient

from zorya.server.main import app
from zorya.models.policy import Policy
from zorya.models.schedule import Schedule
from zorya.exceptions import DocumentNotFound

API_VERSION = "/api/v1"

client = TestClient(app, raise_server_exceptions=True)

# TODO: Dummy model isntances


def test_time_zones():
    response = client.get("/api/v1/time_zones")
    assert response.status_code == 200
    assert response.json() == {"Timezones": pytz.all_timezones}


def test_add_schedule(
    empty_schedule_array: List[List[int]],
    dummy_schedule_raw: Dict[str, Any],
    assert_dict_equal: Callable[[Dict, Dict], bool],
):
    empty_schedule_array[0][0] = 1
    dummy_schedule_raw["ndarray"] = empty_schedule_array

    response = client.post(
        "/api/v1/add_schedule",
        json=dummy_schedule_raw,
    )
    assert response.status_code == 200

    schedule = Schedule.get_by_name(dummy_schedule_raw["name"])

    assert_dict_equal(schedule.api_dict(), dummy_schedule_raw)


def test_add_schedule_default_schedule(
    dummy_schedule_raw: Dict[str, Any],
    assert_dict_equal: Callable[[Dict, Dict], bool],
):
    response = client.post(
        "/api/v1/add_schedule",
        json=dummy_schedule_raw,
    )
    assert response.status_code == 200

    schedule = Schedule.get_by_name("test-schedule")

    assert_dict_equal(schedule.api_dict(), dummy_schedule_raw)


def test_get_schedule_success(
    dummy_schedule_raw: Dict[str, Any],
    assert_dict_equal: Callable[[Dict, Dict], bool],
):
    Schedule(**dummy_schedule_raw).set()

    response = client.get(
        API_VERSION + f"/get_schedule?schedule={dummy_schedule_raw['name']}"
    )
    body = response.json()

    assert response.status_code == 200, body

    assert_dict_equal(body, dummy_schedule_raw)


def test_get_schedule_not_found():
    response = client.get(API_VERSION + "/get_schedule?schedule=random-name")

    assert response.status_code == 404


def test_list_schedules():
    names = ["one", "two", "three"]

    [Schedule(name=x, timezone="UTC").set() for x in names]

    response = client.get(API_VERSION + "/list_schedules")

    assert response.status_code == 200
    assert set(response.json()) == set(names)


def test_del_schedule_not_found():
    response = client.get(API_VERSION + "/del_schedule?schedule=random-name")
    assert response.status_code == 404


def test_del_schedule_success():
    name = "test-schedule"
    Schedule(name=name, timezone="UTC").set()

    response = client.get(API_VERSION + f"/del_schedule?schedule={name}")

    assert response.status_code == 200

    with pytest.raises(DocumentNotFound):
        Schedule.get_by_name(name)


def test_add_policy(
    dummy_policy_raw: Dict[str, Any],
    assert_dict_equal: Callable[[Dict, Dict], bool],
):
    Schedule(
        name=dummy_policy_raw["schedulename"],
        timezone="UTC",
    ).set()

    response = client.post(
        "/api/v1/add_policy",
        json=dummy_policy_raw,
    )
    assert response.status_code == 200

    policy = Policy.get_by_name(dummy_policy_raw["name"])

    assert_dict_equal(dummy_policy_raw, policy.dict())


def test_add_policy_missing_schedule(
    dummy_policy_raw: Dict[str, Any],
):
    response = client.post(
        "/api/v1/add_policy",
        json=dummy_policy_raw,
    )
    assert response.status_code == 404


def test_get_policy_success(
    dummy_policy_raw: Dict[str, Any],
    assert_dict_equal: Callable[[Dict, Dict], bool],
):
    Policy(**dummy_policy_raw).set()

    response = client.get(
        API_VERSION + f"/get_policy?policy={dummy_policy_raw['name']}"
    )
    body = response.json()

    assert_dict_equal(dummy_policy_raw, body)


def test_get_policy_not_found():
    response = client.get(API_VERSION + "/get_policy?policy=random-name")
    body = response.json()

    assert response.status_code == 404, body


def test_list_policies(
    dummy_policy_raw: Dict[str, Any],
):
    names = ["one", "two", "three"]

    [Policy(**{**dummy_policy_raw, "name": x}).set() for x in names]

    response = client.get(API_VERSION + "/list_policies")

    assert response.status_code == 200
    assert set(response.json()) == set(names)


def test_del_policy_not_found():
    response = client.get(API_VERSION + "/del_policy?policy=random-name")
    assert response.status_code == 404


def test_del_policy_success(
    dummy_policy_raw: Dict[str, Any],
):
    Policy(**dummy_policy_raw).set()

    response = client.get(
        API_VERSION + f"/del_policy?policy={dummy_policy_raw['name']}"
    )

    assert response.status_code == 200

    with pytest.raises(DocumentNotFound):
        Policy.get_by_name(dummy_policy_raw["name"])
