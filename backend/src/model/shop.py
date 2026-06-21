from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelOnlyId


class Shop(BaseModelOnlyId):
    """Модель для предоставления названия онлайн магазина: id, name, url
    url - ссылка по которой будет производиться поиск
    """
    __tablename__ = "shop"
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    url: Mapped[str] = mapped_column(String(150), nullable=False)
    shop_shop_link = relationship('ShopLink', back_populates='shop', cascade='all, delete-orphan')

    def __str__(self):
        return f'<shop>: {self.id} {self.name}'
