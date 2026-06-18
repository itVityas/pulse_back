from datetime import date as idate, datetime

from pydantic import BaseModel
from schema.currency import CurrencyFullSchema
from schema.shop import ShopSmallSchema


class FileUploadSchema(BaseModel):
    currency_id: int
    shop_id: int
    date: idate


class FileUploadModelResponseSchema(BaseModel):
    id: int
    file_name: str
    currency: CurrencyFullSchema
    shop: ShopSmallSchema
    date: idate
    created_at: datetime

    class Config:
        from_attributes = True
