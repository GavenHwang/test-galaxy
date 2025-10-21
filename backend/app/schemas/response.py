from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class ResponseSchema(BaseModel, Generic[T]):
    code: int = 200
    data: Optional[T] = None
    msg: str = "success"

    @classmethod
    def success(cls, data: T = None, msg: str = "success") -> "ResponseSchema[T]":
        return cls(data=data, msg=msg)

    @classmethod
    def error(cls, msg: str = "error", code: int = 400) -> "ResponseSchema[T]":
        return cls(code=code, msg=msg)