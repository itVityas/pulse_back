from typing import List, TypeVar, Generic

from pydantic import BaseModel, Field, field_validator


T = TypeVar('T')


class PaginationParamsSchema(BaseModel):
    page: int = Field(default=1, ge=1, description='Номер страницы, начинается с 1')
    page_size: int = Field(default=20, ge=-1, le=100, description='Размер страницы, с 1 до 100')

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def filters(self) -> dict:
        fields = vars(self)
        fields = [f for f in fields if not f.startswith('_') and f not in ['page', 'page_size', 'sort_field', 'sort_order', 'filters', 'offset', 'limit']]
        return {f: getattr(self, f) for f in fields}

    def get_count_pages(self, total):
        return total // self.page_size + (1 if total % self.page_size else 0)


class PaginationSortParamsSchema(BaseModel):
    page: int = Field(default=1, ge=1, description='Номер страницы, начинается с 1')
    page_size: int = Field(default=20, ge=-1, le=100, description='Размер страницы, с 1 до 100')
    sort_field: str = Field(default='id', description='Поле для сортировки')
    sort_order: str = Field(default='asc', description='Порядок сортировки: asc или desc')

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def filters(self) -> dict:
        fields = vars(self)
        fields = [f for f in fields if not f.startswith('_') and f not in ['page', 'page_size', 'sort_field', 'sort_order', 'filters', 'offset', 'limit']]
        return {f: getattr(self, f) for f in fields}

    @field_validator('sort_order')
    def validate_sort_order(cls, v):
        if v.lower() not in ['asc', 'desc']:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v.lower()

    def get_count_pages(self, total):
        return total // self.page_size + (1 if total % self.page_size else 0)


class PaginationResponseSchema(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
