from datetime import date
from typing import Literal, List, Union, Optional

from pydantic import BaseModel, RootModel

from .pagination import PaginationSortParamsSchema


class RangeDataSchema(BaseModel):
    start: date
    end: date


class MinMaxDataSchema(BaseModel):
    min: float
    max: float


class DateRangeSchema(BaseModel):
    field: Literal['date_range']
    data: RangeDataSchema


class DiagonalSchema(BaseModel):
    field: Literal['diagonal']
    data: MinMaxDataSchema


class ListDataSchema(BaseModel):
    field: Literal[
        "shops",
        "brands",
        "os",
        "screen_resolutions",
        "matrix_types",
        "refresh_rate",
        "currency",
    ]
    data: List[Union[str, int]]


FilterItem = Union[DateRangeSchema, DiagonalSchema, ListDataSchema]


class MainChartRequestSchema(RootModel):
    root: List[FilterItem]


class MainChartTVMinPriceRequest(PaginationSortParamsSchema):
    name: Optional[str] = None
    name__ne: Optional[str] = None
    name__icontains: Optional[str] = None
    name__istartswith: Optional[str] = None
    name__iendswith: Optional[str] = None


class MainChartValuesTVMinPrice(BaseModel):
    min_price: float
    shop: str
    link: str


class MainChartTVMinPriceResponse(BaseModel):
    tv_id: int
    name: str
    values: List[MainChartValuesTVMinPrice]
