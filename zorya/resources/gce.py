"""Interactions with compute engine."""
from typing import Generator

from zorya.resources.gcp_base import GCPBase
from zorya.models.gce_instance import GCEInstance


class GoogleComputEngine(GCPBase):
    def change_status(self) -> None:
        self.logger("running state change for compute instances")

        if self.state_change.action == 1:
            action = self.start_instance
        else:
            action = self.stop_instance

        count = 0
        for instance in self.list_instances():
            count += 1
            action(instance.zone, instance.name)

        self.logger(f"{count} compute instances patched")

    def stop_instance(self, zone: str, instance_name: str) -> None:
        logger = self.logger.refine(instance_name=instance_name, zone=zone)
        logger("stopping compute instance")

        res = self.authed_session.post(
            "https://compute.googleapis.com/compute/v1"
            f"/projects/{self.state_change.project}"
            f"/zones/{zone}"
            f"/instances/{instance_name}"
            "/stop"
        )
        if res.status_code >= 400:
            logger("failed stopping instance", error=res.json())

    def start_instance(self, zone: str, instance_name: str) -> None:
        logger = self.logger.refine(instance_name=instance_name, zone=zone)
        logger("starting compute instance")

        res = self.authed_session.post(
            "https://compute.googleapis.com/compute/v1"
            f"/projects/{self.state_change.project}"
            f"/zones/{zone}"
            f"/instances/{instance_name}"
            "/start"
        )
        if res.status_code >= 400:
            logger("failed starting instance", error=res.json())

    def list_instances(self) -> Generator[GCEInstance, None, None]:
        self.logger("listing instance")

        tag_filter = (
            f"labels.{self.state_change.tagkey}={self.state_change.tagvalue}"
        )

        res = self.authed_session.get(
            f"https://compute.googleapis.com/compute/v1"
            f"/projects/{self.state_change.project}"
            "/aggregated/instances"
            f"?filter={tag_filter}"
        )

        res.raise_for_status()
        for x in res.json().get("items", []):
            yield GCEInstance(**x)
