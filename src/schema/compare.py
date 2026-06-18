from typing import Optional

from pydantic import BaseModel


class PricePartSchema(BaseModel):
    card_price: Optional[float] = None
    discount_price: Optional[float] = None
    full_price: Optional[float] = None


class CompareResponseSchema(BaseModel):
    shop_name: str
    prices: PricePartSchema
    alter_percentage: float
    min_price: float
    link: str
