from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelOnlyId


class TV(BaseModelOnlyId):
    """Модель для описания телевизора: id, name, os_id, screen_resolution_id,
    brand_id, matrix_type_id, category_id, color, description, refresh_rate
    """
    __tablename__ = "tv"

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    os_id: Mapped[int] = mapped_column(ForeignKey('os.id'), nullable=True, index=True)
    os = relationship("OS", back_populates='tv_os')
    screen_resolution_id: Mapped[int] = mapped_column(
        ForeignKey('screen_resolution.id'),
        nullable=True,
        index=True)
    screen_resolution = relationship('ScreenResolution', back_populates='tv_screen_resolution')
    brand_id: Mapped[int] = mapped_column(ForeignKey('brand.id'), nullable=True, index=True)
    brand = relationship('Brand', back_populates='tv_brand')
    matrix_type_id: Mapped[int] = mapped_column(ForeignKey('matrix_type.id'), nullable=True, index=True)
    matrix_type = relationship('MatrixType', back_populates='tv_matrix_type')
    color: Mapped[str] = mapped_column(String(20), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    refresh_rate: Mapped[int] = mapped_column(nullable=True, index=True)
    diagonal: Mapped[int] = mapped_column(nullable=True, index=True)
    tv_shop_link = relationship("ShopLink", back_populates='tv', cascade='all, delete-orphan')

    def __str__(self):
        return f'<tv>: {self.id} {self.name}'
