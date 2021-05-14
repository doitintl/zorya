"""gcp_base.py"""
import abc
import google.auth
from google.auth.transport.requests import AuthorizedSession
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from zorya.logging import Logger
from zorya.model.state_change import StateChange


class GCPBase:
    def __init__(
        self,
        state_change: StateChange,
        logger: Logger = None,
    ) -> None:
        self.state_change = state_change
        self.logger = logger or Logger()

    @property
    def authed_session(self) -> requests.Session:
        if not self._authed_session:
            credentials, _ = google.auth.default()
            self._authed_session = AuthorizedSession(credentials)
            retries = Retry(
                total=8,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504],
            )
            self._authed_session.mount(
                "http://", HTTPAdapter(max_retries=retries)
            )
        return self._authed_session
