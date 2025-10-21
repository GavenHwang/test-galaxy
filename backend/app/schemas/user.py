from pydantic import BaseModel
from typing import List, Optional

# schemas/menu.py 或在你的 schema 文件中
import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class UserCreateSchema(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="用户名：2-20位字母、数字、下划线，必须以字母开头"
    )
    role: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="角色名称"
    )


class MenuTreeSchema(BaseModel):
    path: str
    label: str
    icon: Optional[str] = None
    children: List['MenuTreeSchema'] | None = []


# 防止 Pydantic 提前解析问题，可在外部使用 model_config
MenuTreeSchema.model_rebuild()


# 用户输出用的 Schema
class UserOut(BaseModel):
    id: int
    name: str
    role: str  # 角色名称（不是 ID）
    state: int  # is_active -> state
    create_time: str
    last_time: Optional[str] = None

    class Config:
        from_attributes = True  # Tortoise 兼容 ORM 模式


# 分页结果封装
class PaginatedData(BaseModel):
    data: List[UserOut]
    total: int


class UserIdSchema(BaseModel):
    user_id: int
