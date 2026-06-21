from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelOnlyId


class OS(BaseModelOnlyId):
    """Модель для предоставления операционной системы телевизора: id, name
    """
    __tablename__ = "os"
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    tv_os = relationship("TV", back_populates='os', cascade='all, delete-orphan')

    def __str__(self):
        return f'<os>: {self.id} {self.name}'
