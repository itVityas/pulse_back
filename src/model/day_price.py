from datetime import date as idate

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelOnlyId


class DayPrice(BaseModelOnlyId):
    """Модель для цен на товары: id, shop_link_id, price, discount_price, card_price
    """
    __tablename__ = 'day_price'
    shop_link_id: Mapped[int] = mapped_column(
        ForeignKey('shop_link.id'),
        nullable=False,
        index=True)
    shop_link = relationship("ShopLink", back_populates='price_shop_link')
    currency_id: Mapped[int] = mapped_column(
        ForeignKey('currency.id'),
        nullable=False,
        index=True)
    currency = relationship('Currency', back_populates='currency_shop_link')
    price: Mapped[float] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[idate] = mapped_column(
        insert_default=func.now(),
        nullable=False,
        index=True)

    def __str__(self):
        return f'<DayPrice>: {self.id}'
