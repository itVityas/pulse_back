from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelOnlyId


class Brand(BaseModelOnlyId):
    """Модель для бренда товара: id, name, country
    """
    __tablename__ = "brand"
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(50), nullable=True)
    tv_brand = relationship("TV", back_populates='brand', cascade='all, delete-orphan')

    def __str__(self):
        return f'<brand>: {self.id} {self.name}'
