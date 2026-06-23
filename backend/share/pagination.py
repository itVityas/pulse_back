from pydantic import BaseModel
from fastapi import Query


class PaginationParams(BaseModel):
    page: int = Query(1, ge=1, description="Page number")
    page_size: int = Query(10, ge=1, le=100, description="Page size")

    class Config:
        arbitrary_types_allowed = True
