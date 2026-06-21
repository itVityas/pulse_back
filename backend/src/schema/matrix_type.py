from typing import Optional

from pydantic import BaseModel

from .pagination import PaginationSortParamsSchema


class MatrixTypeSmallSchema(BaseModel):
    name: str

    class Config:
        from_attributes = True


class MatrixTypeUpdateSchema(BaseModel):
    name: Optional[str] = None


class MatrixTypeFullSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class MatrixTypeParamsSchema(PaginationSortParamsSchema):
    id: Optional[int] = None
    name: Optional[str] = None
    name__ne: Optional[str] = None
    name__icontains: Optional[str] = None
    name__istartswith: Optional[str] = None
    name__iendswith: Optional[str] = None
