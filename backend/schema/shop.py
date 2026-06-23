from typing import Optional

from pydantic import BaseModel

from .pagination import PaginationSortParamsSchema


class ShopSmallSchema(BaseModel):
    name: str
    url: str

    class Config:
        from_attributes = True


class ShopUpdateShema(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True


class ShopFullSchema(BaseModel):
    id: int
    name: str
    url: str

    class Config:
        from_attributes = True


class ShopParamsFilterSchema(PaginationSortParamsSchema):
    id: Optional[int] = None
    name: Optional[str] = None
    name__ne: Optional[str] = None
    name__icontains: Optional[str] = None
    name__istartswith: Optional[str] = None
    name__iendswith: Optional[str] = None
    url: Optional[str] = None
