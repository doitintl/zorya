"""gcp_base.py"""
from __future__ import annotations

import abc
from typing import TYPE_CHECKING

import google.auth
from google.auth.transport.requests import AuthorizedSession

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from zorya.logging import Logger

if TYPE_CHECKING:
    import requests
    from zorya.models.state_change import StateChange


class GCPBase:
    def __init__(
        self,
        state_change: StateChange,
        logger: Logger = None,
        authed_session: requests.Session = None,
    ) -> None:
        self.state_change = state_change
        self.logger = logger or Logger()

        self.authed_session = authed_session
        if not self.authed_session:
            credentials, _ = google.auth.default()
            self.authed_session = AuthorizedSession(credentials)
            retries = Retry(
                total=8,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504],
            )
            self.authed_session.mount(
                "http://", HTTPAdapter(max_retries=retries)
            )

    @abc.abstractmethod
    def change_status(self) -> None:
        pass
