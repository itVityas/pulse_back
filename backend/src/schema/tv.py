from typing import Optional

from pydantic import BaseModel

from .pagination import PaginationSortParamsSchema
from .os import OSFullSchema
from .screen_resolution import ScreenResolutionFullSchema
from .brand import BrandFullSchema
from .matrix_type import MatrixTypeFullSchema


class TVUpdateSchema(BaseModel):
    name: Optional[str] = None
    os_id: Optional[int] = None
    screen_resolution_id: Optional[int] = None
    brand_id: Optional[int] = None
    matrix_type_id: Optional[int] = None
    color: Optional[str] = None
    description: Optional[str] = None
    refresh_rate: Optional[int] = None
    diagonal: Optional[int] = None

    class Config:
        from_attributes = True


class TVPOSTSchema(BaseModel):
    name: str
    os_id: Optional[int] = None
    screen_resolution_id: Optional[int] = None
    brand_id: Optional[int] = None
    matrix_type_id: Optional[int] = None
    color: Optional[str] = None
    description: Optional[str] = None
    refresh_rate: Optional[int] = None
    diagonal: Optional[int] = None

    class Config:
        from_attributes = True


class TVSmallResponseSchema(BaseModel):
    id: int
    name: str
    os_id: Optional[int] = None
    screen_resolution_id: Optional[int] = None
    brand_id: Optional[int] = None
    matrix_type_id: Optional[int] = None
    color: Optional[str] = None
    description: Optional[str] = None
    refresh_rate: Optional[int] = None
    diagonal: Optional[int] = None

    class Config:
        from_attributes = True


class TVFilterSchema(PaginationSortParamsSchema):
    id: Optional[int] = None
    name: Optional[str] = None
    name__ne: Optional[str] = None
    name__icontains: Optional[str] = None
    name__istartswith: Optional[str] = None
    name__iendswith: Optional[str] = None
    os_id: Optional[int] = None
    screen_resolution_id: Optional[int] = None
    brand_id: Optional[int] = None
    matrix_type_id: Optional[int] = None
    color: Optional[str] = None
    refresh_rate: Optional[int] = None
    diagonal: Optional[int] = None


class TVFullResponceSchema(BaseModel):
    id: int
    name: str
    os: Optional[OSFullSchema] = None
    screen_resolution: Optional[ScreenResolutionFullSchema] = None
    brand: Optional[BrandFullSchema] = None
    matrix_type: Optional[MatrixTypeFullSchema] = None
    color: Optional[str] = None
    description: Optional[str] = None
    refresh_rate: Optional[int] = None
    diagonal: Optional[int] = None

    class Config:
        from_attributes = True
