"""Interactions with compute engine."""
from typing import List

import pydantic

from zorya.resources.gcp_base import GCPBase


class CloudSQLInstance(pydantic.BaseModel):
    name: str


class CloudSql(GCPBase):
    def change_status(self):
        self.logger("running state change for CloudSQL instances")

        for instance in self.list_instances():
            logger = self.logger.refine(instance=instance)
            if int(self.change_status.action) == 1:
                logger("Starting CloudSQL instance", instance=instance)
                self.start_instance(instance.name)
            else:
                logger("Stopping CloudSQL instance", instance=instance)
                self.stop_instance(instance.name)

    def stop_instance(self, instance: str) -> None:
        res = self.authed_session.get(
            "https://sqladmin.googleapis.com/sql/v1beta4"
            f"/projects/{self.change_status.project}"
            f"/instances/{instance}",
        )
        res.raise_for_status()
        prev_instance_data = res.json()

        patch_body = {
            "settings": {
                "settingsVersion": prev_instance_data["settings"][
                    "settingsVersion"
                ],
                "activationPolicy": "NEVER",
            }
        }

        res = self.authed_session.patch(
            "https://sqladmin.googleapis.com/sql/v1beta4"
            f"/projects/{self.change_status.project}"
            f"/instances/{instance}",
            data=patch_body,
        )
        res.raise_for_status()

    def start_instance(self, instance: str) -> None:
        res = self.authed_session.get(
            "https://sqladmin.googleapis.com/sql/v1beta4"
            f"/projects/{self.change_status.project}"
            f"/instances/{instance}",
        )

        res.raise_for_status()
        prev_instance_data = res.json()

        patch_body = {
            "settings": {
                "settingsVersion": prev_instance_data["settings"][
                    "settingsVersion"
                ],
                "activationPolicy": "ALWAYS",
            }
        }

        res = self.authed_session.patch(
            "https://sqladmin.googleapis.com/sql/v1beta4"
            f"/projects/{self.change_status.project}"
            f"/instances/{instance}",
            data=patch_body,
        )
        res.raise_for_status()

    def list_instances(self) -> List[CloudSQLInstance]:
        tag_filter = (
            "settings.userLabels."
            f"{self.state_change.tagkey}={self.state_change.tagvalue}"
        )

        res = self.authed_session.get(
            "https://sqladmin.googleapis.com/sql/v1beta4"
            f"/projects/{self.state_change.project}"
            "/instances"
            f"?filter={tag_filter}"
        )
        res.raise_for_status()

        for x in res.json().get("items", []):
            yield CloudSQLInstance(**x)
