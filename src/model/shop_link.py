from sqlalchemy import ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class ShopLink(BaseModel):
    """Модель для ссылок по которым мониторятся цены: id, shop_id, tv_id, link, is_active
    """
    __tablename__ = 'shop_link'
    shop_id: Mapped[int] = mapped_column(ForeignKey('shop.id'), nullable=False)
    shop = relationship('Shop', back_populates='shop_shop_link')
    tv_id: Mapped[int] = mapped_column(ForeignKey('tv.id'), nullable=False)
    tv = relationship('TV', back_populates='tv_shop_link')
    link: Mapped[str] = mapped_column(Text(), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), insert_default=True)
    price_shop_link = relationship("DayPrice", back_populates='shop_link', cascade='all, delete-orphan')

    def __str__(self):
        return f'<Currency>: {self.id}'
