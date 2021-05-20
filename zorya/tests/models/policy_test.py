"""policy_test.py"""
import json
from unittest import mock
from typing import Dict, Any

import pytest

from zorya.models.policy import Policy
from zorya.models.schedule import Schedule
from zorya.logging import Logger
from zorya.settings import settings
from zorya.exceptions import DocumentNotFound


@mock.patch("google.cloud.pubsub.PublisherClient.publish")
def test_check_one_policy_no_change(
    mock_pubusub_publish: mock.Mock,
    dummy_policy_raw: Dict[str, Any],
    dummy_schedule_raw: Dict[str, Any],
):
    policy = Policy(**dummy_policy_raw)
    Schedule(**dummy_schedule_raw).set()

    policy.check_one(logger=Logger())

    assert mock_pubusub_publish.call_args_list == []


@mock.patch("google.cloud.pubsub.PublisherClient.publish")
@mock.patch(
    "zorya.models.schedule.Schedule.changed",
    new_callable=mock.PropertyMock,
    return_value=True,
)
def test_check_one_policy(
    changed_mock: mock.Mock,
    mock_pubusub_publish: mock.Mock,
    dummy_policy_raw: Dict[str, Any],
    dummy_schedule_raw: Dict[str, Any],
):
    policy = Policy(**dummy_policy_raw)
    Schedule(**dummy_schedule_raw).set()

    policy.check_one(logger=Logger())

    expected_calls = [
        mock.call(
            f"projects/{settings.project_id}/topics/{settings.topic_id}",
            data=json.dumps(
                {
                    "project": project,
                    "tagkey": tagkey,
                    "tagvalue": tagvalue,
                    "action": 0,
                }
            ).encode("utf-8"),
        )
        for tagkeyvalue in policy.tags
        for tagkey, tagvalue in iter(tagkeyvalue.items())
        for project in policy.projects
    ]

    assert mock_pubusub_publish.call_args_list == expected_calls


def test_check_one_schedule_not_found():
    policy = Policy(name="test-policy", schedulename="test-schedule")

    with pytest.raises(DocumentNotFound):
        policy.check_one(logger=Logger())
