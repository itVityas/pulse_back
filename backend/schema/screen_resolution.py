from typing import Optional

from pydantic import BaseModel

from .pagination import PaginationSortParamsSchema


class ScreenResolutionSmallSchema(BaseModel):
    name: str
    width: int
    height: int

    class Config:
        from_attributes = True


class ScreenResolutionUpdateSchema(BaseModel):
    name: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

    class Config:
        from_attributes = True


class ScreenResolutionFullSchema(BaseModel):
    id: int
    name: str
    width: int
    height: int

    class Config:
        from_attributes = True


class ScreenResolutionParamFilterSchema(PaginationSortParamsSchema):
    id: Optional[int] = None
    name: Optional[str] = None
    name__ne: Optional[str] = None
    name__icontains: Optional[str] = None
    name__istartswith: Optional[str] = None
    name__iendswith: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
