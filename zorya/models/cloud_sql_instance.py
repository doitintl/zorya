import pydantic


class CloudSQLInstance(pydantic.BaseModel):
    name: str
