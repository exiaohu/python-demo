from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    data: T
    message: str = "Success"

    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    size: int

    model_config = ConfigDict(from_attributes=True)
