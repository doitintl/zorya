from unittest import mock
from typing import Dict, Any, List, Tuple, Callable

import pytest
import requests

from zorya.models.gke_cluster import GoogleKubernetesEngineCluster

from zorya.models.gke_node_pool import GKENodePool
from zorya.models.state_change import StateChange
from zorya.resources.gke import GoogleKubernetesEngine
from zorya.logging import Logger


@pytest.fixture
def raw_cluster_list():
    return [
        {
            "name": name,
            "nodePools": [
                {
                    "name": "name1",
                    "instanceGroupUrls": ["url1"],
                    "num_nodes": 3,
                }
            ],
            "resourceLabels": {"tagkey": "tagvalue"},
        }
        for name in ["name1", "name2", "name3"]
    ]


@pytest.fixture
def gke_resource__mocked_req_sess(
    state_change_raw: Dict[str, Any],
):
    state_change = StateChange(**state_change_raw)
    mock_authed_session = mock.MagicMock(spec=requests.Session)

    return (
        GoogleKubernetesEngine(
            state_change,
            authed_session=mock_authed_session,
        ),
        mock_authed_session,
    )


@pytest.fixture
def gke_resource(
    gke_resource__mocked_req_sess: Tuple[
        GoogleKubernetesEngine, mock.MagicMock
    ],
):
    gke_resource, _ = gke_resource__mocked_req_sess

    return gke_resource


@pytest.fixture
def mocked_req_sess(
    gke_resource__mocked_req_sess: Tuple[
        GoogleKubernetesEngine, mock.MagicMock
    ],
):
    _, mocked_req_sess = gke_resource__mocked_req_sess

    return mocked_req_sess


@pytest.fixture
def dummy_gke_cluster():
    return GoogleKubernetesEngineCluster(
        name="name",
        resourceLabels={},
        nodePools=[
            GKENodePool(name="name", instanceGroupUrls=["instance_group_url"])
        ],
    )


def test_list_instances(
    gke_resource: GoogleKubernetesEngine,
    mocked_req_sess: mock.MagicMock,
    raw_cluster_list: List[Dict[str, Any]],
    assert_dict_equal: Callable[[Dict, Dict], bool],
):
    mocked_req_sess.get().json.return_value = {"clusters": raw_cluster_list}

    list_clusters_generator = gke_resource.list_clusters()

    count = 0
    for instance in list_clusters_generator:
        assert isinstance(instance, GoogleKubernetesEngineCluster)
        assert_dict_equal(instance.dict(), raw_cluster_list[count])
        count += 1

    assert len(raw_cluster_list) == count

    mocked_req_sess.get.assert_has_calls(
        [
            mock.call(
                "https://container.googleapis.com/v1"
                f"/projects/{gke_resource.state_change.project}"
                "/locations/-"
                "/clusters"
            )
        ]
    )


def test_get_instancegroup_num_nodes_success(
    gke_resource: GoogleKubernetesEngine,
    mocked_req_sess: mock.MagicMock,
):
    size = 5
    instance_group_url = "instance_group_url"
    mocked_req_sess.get().status_code = 200
    mocked_req_sess.get().json.return_value = {"size": size}

    return_value = gke_resource.get_instancegroup_num_nodes(
        "instance_group_url", Logger()
    )

    assert return_value == size
    mocked_req_sess.get.assert_has_calls([mock.call(instance_group_url)])


def test_get_instancegroup_num_nodes_400_error(
    gke_resource: GoogleKubernetesEngine,
    mocked_req_sess: mock.MagicMock,
):
    instance_group_url = "instance_group_url"
    mocked_req_sess.get().status_code = 400

    return_value = gke_resource.get_instancegroup_num_nodes(
        instance_group_url, Logger()
    )

    assert return_value == 0
    mocked_req_sess.get.assert_has_calls([mock.call(instance_group_url)])


def test_get_instancegroup_num_nodes_no_size(
    gke_resource: GoogleKubernetesEngine,
    mocked_req_sess: mock.MagicMock,
):
    size = 0
    instance_group_url = "instance_group_url"
    mocked_req_sess.get().status_code = 200
    mocked_req_sess.get().json.return_value = {}

    return_value = gke_resource.get_instancegroup_num_nodes(
        "instance_group_url", Logger()
    )

    assert return_value == size
    mocked_req_sess.get.assert_has_calls([mock.call(instance_group_url)])


def test_match_cluster(
    gke_resource: GoogleKubernetesEngine,
    dummy_gke_cluster: GoogleKubernetesEngineCluster,
):
    gke_resource.state_change.tagkey, gke_resource.state_change.tagvalue = (
        "one",
        "one",
    )
    dummy_gke_cluster.resourceLabels = {"one": "one"}
    assert gke_resource.match_cluster(dummy_gke_cluster) is True

    dummy_gke_cluster.resourceLabels = {"one": "one", "two": "two"}
    assert gke_resource.match_cluster(dummy_gke_cluster) is True

    dummy_gke_cluster.resourceLabels = {}
    assert gke_resource.match_cluster(dummy_gke_cluster) is False

    dummy_gke_cluster.resourceLabels = {"one": "two"}
    assert gke_resource.match_cluster(dummy_gke_cluster) is False

    dummy_gke_cluster.resourceLabels = {"two": "one"}
    assert gke_resource.match_cluster(dummy_gke_cluster) is False

    dummy_gke_cluster.resourceLabels = {"two": "two"}
    assert gke_resource.match_cluster(dummy_gke_cluster) is False


def test_resize_node_pool_success(
    gke_resource: GoogleKubernetesEngine,
    mocked_req_sess: mock.MagicMock,
):
    size = 5
    instance_group_url = "instance_group_url"
    mocked_req_sess.post().status_code = 200

    gke_resource.resize_node_pool(size, instance_group_url, Logger())

    mocked_req_sess.post.assert_has_calls(
        [mock.call(f"{instance_group_url}/resize?size={size}")]
    )


def test_resize_node_pool_400_error(
    gke_resource: GoogleKubernetesEngine,
    mocked_req_sess: mock.MagicMock,
):
    size = 5
    instance_group_url = "instance_group_url"
    mocked_req_sess.post().status_code = 400

    gke_resource.resize_node_pool(size, instance_group_url, Logger())

    mocked_req_sess.post.assert_has_calls(
        [mock.call(f"{instance_group_url}/resize?size={size}")]
    )
