from datetime import date

from pydantic import BaseModel
from typing import List


class CompareRequestSchema(BaseModel):
    date_start: date
    date_end: date


class PricePartSchema(BaseModel):
    name: str
    price: float


class CompareResponseSchema(BaseModel):
    shop_name: str
    prices: List[PricePartSchema]
    alter_percentage: float
    link: str
