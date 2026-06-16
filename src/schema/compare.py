from pydantic import BaseModel
from typing import List


class PricePartSchema(BaseModel):
    name: str
    price: float


class CompareResponseSchema(BaseModel):
    shop_name: str
    prices: List[PricePartSchema]
    alter_percentage: float
    link: str
