from unittest import mock
from typing import Dict, Any, Callable, List, Tuple

import requests
import pytest

from zorya.resources.gce import GoogleComputEngine
from zorya.models.gce_instance import GCEInstance
from zorya.models.state_change import StateChange


@pytest.fixture
def raw_instance_list():
    return [
        {"name": "one", "zone": "zone"},
        {"name": "two", "zone": "zone"},
        {"name": "three", "zone": "zone"},
    ]


@pytest.fixture
def gce_resource__mocked_req_sess(
    state_change_raw: Dict[str, Any],
):
    state_change = StateChange(**state_change_raw)
    mock_authed_session = mock.MagicMock(spec=requests.Session)

    return (
        GoogleComputEngine(
            state_change,
            authed_session=mock_authed_session,
        ),
        mock_authed_session,
    )


@pytest.fixture
def gce_resource(
    gce_resource__mocked_req_sess: Tuple[GoogleComputEngine, mock.MagicMock],
):
    gce_resource, _ = gce_resource__mocked_req_sess

    return gce_resource


@pytest.fixture
def mocked_req_sess(
    gce_resource__mocked_req_sess: Tuple[GoogleComputEngine, mock.MagicMock],
):
    _, mocked_req_sess = gce_resource__mocked_req_sess

    return mocked_req_sess


def test_list_instances(
    gce_resource: GoogleComputEngine,
    mocked_req_sess: mock.MagicMock,
    raw_instance_list: List[Dict[str, Any]],
    assert_dict_equal: Callable[[Dict, Dict], bool],
):
    mocked_req_sess.get().json.return_value = {"items": raw_instance_list}

    list_instances_generator = gce_resource.list_instances()

    count = 0
    for instance in list_instances_generator:
        assert isinstance(instance, GCEInstance)
        assert_dict_equal(instance.dict(), raw_instance_list[count])
        count += 1

    assert len(raw_instance_list) == count

    mocked_req_sess.get.assert_has_calls(
        [
            mock.call(
                "https://compute.googleapis.com/compute/v1"
                f"/projects/{gce_resource.state_change.project}/aggregated/instances"
                f"?filter=labels.{gce_resource.state_change.tagkey}"
                f"={gce_resource.state_change.tagvalue}"
            )
        ]
    )


def test_list_instances_http_error(
    gce_resource: GoogleComputEngine,
    mocked_req_sess: mock.MagicMock,
):
    mocked_req_sess.get().raise_for_status.side_effect = (
        requests.exceptions.HTTPError()
    )

    list_instances_generator = gce_resource.list_instances()

    with pytest.raises(requests.exceptions.HTTPError):
        next(list_instances_generator)


def test_start_instance_success(
    gce_resource: GoogleComputEngine,
    mocked_req_sess: mock.MagicMock,
):
    zone, instance_name = "zone", "instance_name"
    mocked_req_sess.post().status_code = 200

    return_value = gce_resource.start_instance(zone, instance_name)

    assert return_value is None

    mocked_req_sess.post.assert_has_calls(
        [
            mock.call(
                "https://compute.googleapis.com/compute/v1"
                f"/projects/{gce_resource.state_change.project}"
                f"/zones/{zone}"
                f"/instances/{instance_name}"
                "/start"
            )
        ]
    )


def test_start_instance_400_error(
    gce_resource: GoogleComputEngine,
    mocked_req_sess: mock.MagicMock,
):
    zone, instance_name = "zone", "instance_name"
    mocked_req_sess.post().status_code = 400

    return_value = gce_resource.start_instance(zone, instance_name)

    assert return_value is None


def test_stop_instance_success(
    gce_resource: GoogleComputEngine,
    mocked_req_sess: mock.MagicMock,
):
    zone, instance_name = "zone", "instance_name"
    mocked_req_sess.post().status_code = 200

    return_value = gce_resource.stop_instance(zone, instance_name)

    assert return_value is None

    mocked_req_sess.post.assert_has_calls(
        [
            mock.call(
                "https://compute.googleapis.com/compute/v1"
                f"/projects/{gce_resource.state_change.project}"
                f"/zones/{zone}"
                f"/instances/{instance_name}"
                "/stop"
            )
        ]
    )


def test_stop_instance_http_error(
    gce_resource: GoogleComputEngine,
    mocked_req_sess: mock.MagicMock,
):
    zone, instance_name = "zone", "instance_name"
    mocked_req_sess.post().status_code = 400

    return_value = gce_resource.stop_instance(zone, instance_name)

    assert return_value is None


def test_change_status_empty_list(
    gce_resource: GoogleComputEngine,
    mocked_req_sess: mock.MagicMock,
):
    mocked_req_sess.get().json.return_value = {"items": []}

    with mock.patch.object(
        gce_resource, "start_instance"
    ) as mocked_start_instance, mock.patch.object(
        gce_resource, "stop_instance"
    ) as mocked_stop_instance:

        gce_resource.change_status()

        mocked_req_sess.get.assert_has_calls(
            [
                mock.call(
                    "https://compute.googleapis.com/compute/v1"
                    f"/projects/{gce_resource.state_change.project}/aggregated"
                    f"/instances?filter=labels.{gce_resource.state_change.tagkey}"
                    f"={gce_resource.state_change.tagvalue}"
                )
            ]
        )
        mocked_start_instance.assert_not_called()
        mocked_stop_instance.assert_not_called()


def test_change_status_no_list(
    gce_resource: GoogleComputEngine,
    mocked_req_sess: mock.MagicMock,
):
    mocked_req_sess.get().json.return_value = {}

    with mock.patch.object(
        gce_resource, "start_instance"
    ) as mocked_start_instance, mock.patch.object(
        gce_resource, "stop_instance"
    ) as mocked_stop_instance:

        gce_resource.change_status()

        mocked_req_sess.get.assert_has_calls(
            [
                mock.call(
                    "https://compute.googleapis.com/compute/v1"
                    f"/projects/{gce_resource.state_change.project}/aggregated"
                    f"/instances?filter=labels.{gce_resource.state_change.tagkey}"
                    f"={gce_resource.state_change.tagvalue}"
                )
            ]
        )
        mocked_start_instance.assert_not_called()
        mocked_stop_instance.assert_not_called()


def test_change_status_start(
    gce_resource: GoogleComputEngine,
    mocked_req_sess: mock.MagicMock,
    raw_instance_list: List[Dict[str, Any]],
):
    mocked_req_sess.get().json.return_value = {"items": raw_instance_list}

    with mock.patch.object(
        gce_resource, "start_instance"
    ) as mocked_start_instance, mock.patch.object(
        gce_resource, "stop_instance"
    ) as mocked_stop_instance:

        gce_resource.state_change.action = 1
        gce_resource.change_status()

        mocked_req_sess.get.assert_has_calls(
            [
                mock.call(
                    "https://compute.googleapis.com/compute/v1"
                    f"/projects/{gce_resource.state_change.project}/aggregated"
                    f"/instances?filter=labels.{gce_resource.state_change.tagkey}"
                    f"={gce_resource.state_change.tagvalue}"
                )
            ]
        )
        mocked_start_instance.call_count = len(raw_instance_list)
        mocked_stop_instance.assert_not_called()


def test_change_status_stop(
    gce_resource: GoogleComputEngine,
    mocked_req_sess: mock.MagicMock,
    raw_instance_list: List[Dict[str, Any]],
):
    mocked_req_sess.get().json.return_value = {"items": raw_instance_list}

    with mock.patch.object(
        gce_resource, "start_instance"
    ) as mocked_start_instance, mock.patch.object(
        gce_resource, "stop_instance"
    ) as mocked_stop_instance:

        gce_resource.state_change.action = 0
        gce_resource.change_status()

        mocked_req_sess.get.assert_has_calls(
            [
                mock.call(
                    "https://compute.googleapis.com/compute/v1"
                    f"/projects/{gce_resource.state_change.project}/aggregated"
                    f"/instances?filter=labels.{gce_resource.state_change.tagkey}"
                    f"={gce_resource.state_change.tagvalue}"
                )
            ]
        )
        mocked_start_instance.assert_not_called()
        mocked_stop_instance.call_count = len(raw_instance_list)
