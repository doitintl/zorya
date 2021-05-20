"""state_change.py"""
import pydantic

from zorya.resources import ALL_RESOURCES
from zorya.logging import Logger


class StateChange(pydantic.BaseModel):
    tagkey: str
    tagvalue: str
    action: int
    project: str

    def change_state(self, logger: Logger) -> None:
        for resource in ALL_RESOURCES:
            try:
                resource(
                    self,
                    logger=logger,
                ).change_status()
            except Exception as ex:
                logger(
                    f"could not change state for resource {resource.__class__}: {ex}",
                    exception=str(ex),
                )
