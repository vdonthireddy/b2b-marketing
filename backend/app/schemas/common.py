from pydantic import BaseModel
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
