import math
from typing import Annotated, Any, NamedTuple, Self, Sequence

from fastapi import Depends, Query
from pydantic import BaseModel

from src.config import settings


class Pagination(NamedTuple):
    page: int
    size: int

def get_pagination(
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0),
) -> Pagination:
    return Pagination(page, min(settings.API_PAGINATION_MAX_SIZE, size))

PaginationQuery = Annotated[Pagination, Depends(get_pagination)]


class Page[T: Any](BaseModel):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
    
    @classmethod
    def from_paginated_results(cls, items: Sequence[T], total: int, pagination: Pagination) -> Self:
        total_pages = math.ceil(total / max(1, pagination.size))
        return cls(
                items=list(items),
                total=total,
                page=pagination.page,
                size=pagination.size,
                pages=total_pages
        )
