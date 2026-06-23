from typing import Optional

from pydantic import BaseModel

from .pagination import PaginationSortParamsSchema


class CurrencyFullSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CurrencyPaginationParamsSchema(PaginationSortParamsSchema):
    id: Optional[int] = None
    name: Optional[str] = None
    name_ne: Optional[str] = None
    name_icontains: Optional[str] = None
    name_istartswith: Optional[str] = None
    name_iendswith: Optional[str] = None


class CurrencySmallSchema(BaseModel):
    name: str

    class Config:
        from_attributes = True
