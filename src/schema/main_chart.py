from datetime import date
from typing import Literal, List, Union

from pydantic import BaseModel, RootModel


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
