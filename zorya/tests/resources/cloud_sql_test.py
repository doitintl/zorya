from unittest import mock
from typing import Dict, Any, Callable, List, Tuple
from zorya.models.cloud_sql_instance import CloudSQLInstance

import requests
import pytest

from zorya.resources.cloud_sql import CloudSql
from zorya.models.state_change import StateChange


@pytest.fixture
def raw_instance_list():
    return [
        {"name": "instance-name1"},
        {"name": "instance-name2"},
        {"name": "instance-name3"},
    ]


@pytest.fixture
def cloud_sql_resource__mocked_req_sess(
    state_change_raw: Dict[str, Any],
):
    state_change = StateChange(**state_change_raw)
    mock_authed_session = mock.MagicMock(spec=requests.Session)

    return (
        CloudSql(
            state_change,
            authed_session=mock_authed_session,
        ),
        mock_authed_session,
    )


@pytest.fixture
def cloud_sql_resource(
    cloud_sql_resource__mocked_req_sess: Tuple[CloudSql, mock.MagicMock],
):
    cloud_sql_resource, _ = cloud_sql_resource__mocked_req_sess

    return cloud_sql_resource


@pytest.fixture
def mocked_req_sess(
    cloud_sql_resource__mocked_req_sess: Tuple[CloudSql, mock.MagicMock],
):
    _, mocked_req_sess = cloud_sql_resource__mocked_req_sess

    return mocked_req_sess


def test_list_instances(
    cloud_sql_resource: CloudSql,
    mocked_req_sess: mock.MagicMock,
    raw_instance_list: List[Dict[str, Any]],
    assert_dict_equal: Callable[[Dict, Dict], bool],
):
    mocked_req_sess.get().json.return_value = {"items": raw_instance_list}

    list_instances_generator = cloud_sql_resource.list_instances()

    count = 0
    for instance in list_instances_generator:
        assert isinstance(instance, CloudSQLInstance)
        assert_dict_equal(instance.dict(), raw_instance_list[count])
        count += 1

    assert len(raw_instance_list) == count

    mocked_req_sess.get.assert_has_calls(
        [
            mock.call(
                "https://sqladmin.googleapis.com/sql/v1beta4"
                f"/projects/{cloud_sql_resource.state_change.project}"
                "/instances"
                f"?filter=settings.userLabels."
                f"{cloud_sql_resource.state_change.tagkey}="
                f"{cloud_sql_resource.state_change.tagvalue}"
            )
        ]
    )


def test_list_instances_http_error(
    cloud_sql_resource: CloudSql,
    mocked_req_sess: mock.MagicMock,
):
    mocked_req_sess.get().raise_for_status.side_effect = (
        requests.exceptions.HTTPError()
    )

    list_instances_generator = cloud_sql_resource.list_instances()

    with pytest.raises(requests.exceptions.HTTPError):
        next(list_instances_generator)


def test_start_instance_success(
    cloud_sql_resource: CloudSql,
    mocked_req_sess: mock.MagicMock,
):
    instance_name = "instance_name"
    instance_state = {"settings": {"settingsVersion": "settingsVersion"}}
    mocked_req_sess.get().json.return_value = instance_state
    mocked_req_sess.get().status_code = 200
    mocked_req_sess.patch().status_code = 200

    return_value = cloud_sql_resource.start_instance(instance_name)

    assert return_value is None

    mocked_req_sess.patch.assert_has_calls(
        [
            mock.call(
                "https://sqladmin.googleapis.com/sql/v1beta4"
                f"/projects/{cloud_sql_resource.state_change.project}"
                f"/instances/{instance_name}",
                data={
                    "settings": {
                        "settingsVersion": instance_state["settings"][
                            "settingsVersion"
                        ],
                        "activationPolicy": "ALWAYS",
                    }
                },
            )
        ]
    )


def test_start_instance_400_error(
    cloud_sql_resource: CloudSql,
    mocked_req_sess: mock.MagicMock,
):
    instance_name = "instance_name"
    mocked_req_sess.get().status_code = 400

    return_value = cloud_sql_resource.start_instance(instance_name)

    assert return_value is None


def test_stop_instance_success(
    cloud_sql_resource: CloudSql,
    mocked_req_sess: mock.MagicMock,
):
    instance_name = "instance_name"
    instance_state = {"settings": {"settingsVersion": "settingsVersion"}}
    mocked_req_sess.get().json.return_value = instance_state
    mocked_req_sess.get().status_code = 200
    mocked_req_sess.patch().status_code = 200

    return_value = cloud_sql_resource.stop_instance(instance_name)

    assert return_value is None

    mocked_req_sess.patch.assert_has_calls(
        [
            mock.call(
                "https://sqladmin.googleapis.com/sql/v1beta4"
                f"/projects/{cloud_sql_resource.state_change.project}"
                f"/instances/{instance_name}",
                data={
                    "settings": {
                        "settingsVersion": instance_state["settings"][
                            "settingsVersion"
                        ],
                        "activationPolicy": "NEVER",
                    }
                },
            )
        ]
    )
    # zone, instance_name = "zone", "instance_name"
    # mocked_req_sess.post().status_code = 200

    # return_value = gce_resource.stop_instance(zone, instance_name)

    # assert return_value is None

    # mocked_req_sess.post.assert_has_calls(
    #     [
    #         mock.call(
    #             "https://compute.googleapis.com/compute/v1"
    #             f"/projects/{gce_resource.state_change.project}"
    #             f"/zones/{zone}"
    #             f"/instances/{instance_name}"
    #             "/stop"
    #         )
    #     ]
    # )


def test_stop_instance_400_error(
    cloud_sql_resource: CloudSql,
    mocked_req_sess: mock.MagicMock,
):
    instance_name = "instance_name"
    mocked_req_sess.get().status_code = 400

    return_value = cloud_sql_resource.stop_instance(instance_name)

    assert return_value is None


def test_change_status_empty_list(
    cloud_sql_resource: CloudSql,
    mocked_req_sess: mock.MagicMock,
):
    mocked_req_sess.get().json.return_value = {"items": []}

    with mock.patch.object(
        cloud_sql_resource, "start_instance"
    ) as mocked_start_instance, mock.patch.object(
        cloud_sql_resource, "stop_instance"
    ) as mocked_stop_instance:

        cloud_sql_resource.change_status()

        mocked_req_sess.get.assert_has_calls(
            [
                mock.call(
                    "https://sqladmin.googleapis.com/sql/v1beta4"
                    f"/projects/{cloud_sql_resource.state_change.project}"
                    "/instances"
                    f"?filter="
                    "settings.userLabels."
                    f"{cloud_sql_resource.state_change.tagkey}="
                    f"{cloud_sql_resource.state_change.tagvalue}"
                )
            ]
        )
        mocked_start_instance.assert_not_called()
        mocked_stop_instance.assert_not_called()


def test_change_status_no_list(
    cloud_sql_resource: CloudSql,
    mocked_req_sess: mock.MagicMock,
):
    mocked_req_sess.get().json.return_value = {}

    with mock.patch.object(
        cloud_sql_resource, "start_instance"
    ) as mocked_start_instance, mock.patch.object(
        cloud_sql_resource, "stop_instance"
    ) as mocked_stop_instance:

        cloud_sql_resource.change_status()

        mocked_req_sess.get.assert_has_calls(
            [
                mock.call(
                    "https://sqladmin.googleapis.com/sql/v1beta4"
                    f"/projects/{cloud_sql_resource.state_change.project}"
                    "/instances"
                    f"?filter=settings.userLabels."
                    f"{cloud_sql_resource.state_change.tagkey}="
                    f"{cloud_sql_resource.state_change.tagvalue}"
                )
            ]
        )
        mocked_start_instance.assert_not_called()
        mocked_stop_instance.assert_not_called()


def test_change_status_start(
    cloud_sql_resource: CloudSql,
    mocked_req_sess: mock.MagicMock,
    raw_instance_list: List[Dict[str, Any]],
):
    mocked_req_sess.get().json.return_value = {"items": raw_instance_list}

    with mock.patch.object(
        cloud_sql_resource, "start_instance"
    ) as mocked_start_instance, mock.patch.object(
        cloud_sql_resource, "stop_instance"
    ) as mocked_stop_instance:

        cloud_sql_resource.state_change.action = 1
        cloud_sql_resource.change_status()

        mocked_req_sess.get.assert_has_calls(
            [
                mock.call(
                    "https://sqladmin.googleapis.com/sql/v1beta4"
                    f"/projects/{cloud_sql_resource.state_change.project}"
                    "/instances"
                    f"?filter=settings.userLabels."
                    f"{cloud_sql_resource.state_change.tagkey}="
                    f"{cloud_sql_resource.state_change.tagvalue}"
                )
            ]
        )
        mocked_start_instance.call_count = len(raw_instance_list)
        mocked_stop_instance.assert_not_called()


def test_change_status_stop(
    cloud_sql_resource: CloudSql,
    mocked_req_sess: mock.MagicMock,
    raw_instance_list: List[Dict[str, Any]],
):
    mocked_req_sess.get().json.return_value = {"items": raw_instance_list}

    with mock.patch.object(
        cloud_sql_resource, "start_instance"
    ) as mocked_start_instance, mock.patch.object(
        cloud_sql_resource, "stop_instance"
    ) as mocked_stop_instance:

        cloud_sql_resource.state_change.action = 0
        cloud_sql_resource.change_status()

        mocked_req_sess.get.assert_has_calls(
            [
                mock.call(
                    "https://sqladmin.googleapis.com/sql/v1beta4"
                    f"/projects/{cloud_sql_resource.state_change.project}"
                    "/instances"
                    f"?filter=settings.userLabels."
                    f"{cloud_sql_resource.state_change.tagkey}="
                    f"{cloud_sql_resource.state_change.tagvalue}"
                )
            ]
        )
        mocked_start_instance.assert_not_called()
        mocked_stop_instance.call_count = len(raw_instance_list)
