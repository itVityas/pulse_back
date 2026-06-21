from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .pagination import PaginationSortParamsSchema
from .shop import ShopFullSchema
from .tv import TVFullResponceSchema


class ShopLinkUpdateSchema(BaseModel):
    shop_id: Optional[int] = None
    tv_id: Optional[int] = None
    link: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class ShopLinkPostSchema(BaseModel):
    shop_id: int
    tv_id: int
    link: str
    is_active: bool = True

    class Config:
        from_attributes = True


class ShopLinkResponceSmallSchema(BaseModel):
    id: int
    shop_id: int
    tv_id: int
    link: str
    is_active: bool
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ShopLinkResponceFullSchema(BaseModel):
    id: int
    shop: ShopFullSchema
    tv: TVFullResponceSchema
    link: str
    is_active: bool
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ShopLinkFilterSchema(PaginationSortParamsSchema):
    id: Optional[int] = None
    shop_id: Optional[int] = None
    tv_id: Optional[int] = None
    link: Optional[str] = None
    is_active: Optional[bool] = None
