from datetime import date as idate, datetime
from typing import Optional

from pydantic import BaseModel
from schema.currency import CurrencyFullSchema
from schema.shop import ShopSmallSchema
from schema.pagination import PaginationSortParamsSchema


class FileUploadSchema(BaseModel):
    currency_id: int
    shop_id: int
    date: idate


class FileUploadModelResponseSchema(BaseModel):
    id: int
    name: str
    currency: CurrencyFullSchema
    shop: ShopSmallSchema
    date: idate
    created_at: datetime

    class Config:
        from_attributes = True


class FileUploadRequestSchema(PaginationSortParamsSchema):
    id__eq: Optional[int] = None
    date__eq: Optional[idate] = None
