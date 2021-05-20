from unittest import mock

import pytest

from zorya.models.state_change import StateChange
from zorya.resources.gcp_base import GCPBase
from zorya.logging import Logger


def test_change_state(monkeypatch: pytest.MonkeyPatch):
    resources = [mock.MagicMock(spec_set=GCPBase) for _ in range(3)]
    monkeypatch.setattr("zorya.models.state_change.ALL_RESOURCES", resources)

    state_change = StateChange(
        **{
            "tagkey": "tagkey",
            "tagvalue": "tagvalue",
            "action": 1,
            "project": "project",
        }
    )
    logger = Logger()

    state_change.change_state(logger)

    for resource in resources:
        resource.assert_has_calls(
            [
                mock.call(state_change, logger=logger),
                mock.call().change_status(),
            ]
        )
