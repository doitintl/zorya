"""Interactions with compute engine."""
from typing import Generator

from zorya.resources.gcp_base import GCPBase
from zorya.models.cloud_sql_instance import CloudSQLInstance


class CloudSql(GCPBase):
    def change_status(self) -> None:
        self.logger("running state change for CloudSQL instances")

        if self.state_change.action == 1:
            action = self.start_instance
        else:
            action = self.stop_instance

        count = 0
        for instance in self.list_instances():
            count += 1
            action(instance.name)

        self.logger(f"{count} instances patched")

    def stop_instance(self, instance_name: str) -> None:
        logger = self.logger.refine(instance_name=instance_name)
        logger(f"stopping Cloud SQL instance {instance_name!r}")

        res = self.authed_session.get(
            "https://sqladmin.googleapis.com/sql/v1beta4"
            f"/projects/{self.state_change.project}"
            f"/instances/{instance_name}",
        )
        if res.status_code >= 400:
            logger("failed to fetch Cloud SQL instance state")
            return

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
            f"/projects/{self.state_change.project}"
            f"/instances/{instance_name}",
            data=patch_body,
        )
        if res.status_code >= 400:
            logger("failed to stop Cloud SQL instance {instance_name!r}")
            return

    def start_instance(self, instance_name: str) -> None:
        logger = self.logger.refine(instance_name=instance_name)
        logger(f"starting Cloud SQL instance {instance_name!r}")

        res = self.authed_session.get(
            "https://sqladmin.googleapis.com/sql/v1beta4"
            f"/projects/{self.state_change.project}"
            f"/instances/{instance_name}",
        )

        if res.status_code >= 400:
            logger("failed to fetch Cloud SQL instance state")
            return

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
            f"/projects/{self.state_change.project}"
            f"/instances/{instance_name}",
            data=patch_body,
        )

        if res.status_code >= 400:
            logger("failed to start Cloud SQL instance {instance_name!r}")
            return

    def list_instances(self) -> Generator[CloudSQLInstance, None, None]:
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
