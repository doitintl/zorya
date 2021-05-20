import pydantic


class GCEInstance(pydantic.BaseModel):
    name: str
    zone: str
