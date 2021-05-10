"""state_change.py"""
import pydantic


class StateChange(pydantic.BaseModel):
    tagkey: str
    tagvalue: str
    action: int
    project: str
