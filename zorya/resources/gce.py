"""Interactions with compute engine."""
from typing import Generator

from zorya.resources.gcp_base import GCPBase
from zorya.model.gce_instance import GCEInstance


class GoogleComputEngine(GCPBase):
    def change_status(self) -> None:
        self.logger("running state change for compute instances")

        for instance in self.list_instances():
            if int(self.state_change.action) == 1:
                self.logger("Starting compute instance", instance=instance)
                self.start_instance(instance.zone, instance.name)
            else:
                self.logger("Stopping compute instance", instance=instance)
                self.stop_instance(instance.zone, instance.name)

    def stop_instance(self, zone: str, instance_name: str) -> None:
        res = self.authed_session.post(
            "https://compute.googleapis.com/compute/v1"
            f"/projects/{self.state_change.project}"
            f"/zones/{zone}"
            f"/instances/{instance_name}"
            "/stop"
        )
        res.raise_for_status()

    def start_instance(self, zone: str, instance_name: str) -> None:
        res = self.authed_session.post(
            "https://compute.googleapis.com/compute/v1"
            f"/projects/{self.state_change.project}"
            f"/zones/{zone}"
            f"/instances/{instance_name}"
            "/start"
        )
        res.raise_for_status()

    def list_instances(self) -> Generator[GCEInstance, None, None]:
        tag_filter = (
            f"labels.{self.state_change.tagkey}={self.state_change.tagvalue}"
        )
        res = self.authed_session.get(
            f"https://compute.googleapis.com/compute/v1"
            "/projects/{self.change_status.project}"
            "/aggregated/instances"
            f"?filter={tag_filter}"
        )

        res.raise_for_status()
        for x in res.json().get("items", []):
            yield GCEInstance(**x)
