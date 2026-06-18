from datetime import date as datetype

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class FileUpload(BaseModel):
    __tablename__ = "file_upload"
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[datetype] = mapped_column(nullable=False)
    currency_id: Mapped[int] = mapped_column(
        ForeignKey('currency.id'),
        nullable=False,
        index=True)
    shop_id: Mapped[int] = mapped_column(
        ForeignKey('shop.id'),
        nullable=False,
        index=True
    )
