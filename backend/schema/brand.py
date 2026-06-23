from typing import Optional

from pydantic import BaseModel

from .pagination import PaginationSortParamsSchema


class BrandSmallSchema(BaseModel):
    name: str
    country: str

    class Config:
        from_attributes = True


class BrandFullSchema(BaseModel):
    id: int
    name: str
    country: str

    class Config:
        from_attributes = True


class BrandUpdateSchema(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None


class BrandPaginationParamsSchema(PaginationSortParamsSchema):
    id: Optional[int] = None
    name: Optional[str] = None
    name__ne: Optional[str] = None
    name__icontains: Optional[str] = None
    name__istartswith: Optional[str] = None
    name__iendswith: Optional[str] = None
    country: Optional[str] = None
    country__ne: Optional[str] = None
    country__icontains: Optional[str] = None
    country__istartswith: Optional[str] = None
    country__iendswith: Optional[str] = None
