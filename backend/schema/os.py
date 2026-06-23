from typing import Optional

from pydantic import BaseModel

from .pagination import PaginationSortParamsSchema


class OSSmallSchema(BaseModel):
    name: str

    class Config:
        from_attributes = True


class OSFullSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class OSUpdateSchema(BaseModel):
    name: Optional[str] = None

    class Config:
        from_attributes = True


class OSParamFilterSchema(PaginationSortParamsSchema):
    id: Optional[int] = None
    name: Optional[str] = None
    name__ne: Optional[str] = None
    name__icontains: Optional[str] = None
    name__istartswith: Optional[str] = None
    name__iendswith: Optional[str] = None
