from pydantic import BaseModel
from typing import Optional


class ProjectCreateSchema(BaseModel):
    name: str
    desc: Optional[str] = None


class EnvCreateSchema(BaseModel):
    name: str
    domain: str
    need_version: bool = False
    desc: Optional[str] = None
    project_id: int


class RefreshEnvVersionsRequest(BaseModel):
    project_name: str
    env_name: str
