from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelOnlyId


class Currency(BaseModelOnlyId):
    """Модель валюты: id, name
    """
    __tablename__ = "currency"
    name: Mapped[str] = mapped_column(String(3), nullable=False, unique=True, index=True)
    currency_shop_link = relationship('DayPrice', back_populates='currency')

    def __str__(self):
        return f'<Currency>: {self.id} {self.name}'
