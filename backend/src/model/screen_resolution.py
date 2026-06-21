from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelOnlyId


class ScreenResolution(BaseModelOnlyId):
    """Модель для предоставления разрешения экрана телевизора: id, name, width, height
    """
    __tablename__ = 'screen_resolution'
    name: Mapped[str] = mapped_column(String(10), nullable=False, unique=True, index=True)
    width: Mapped[int]
    height: Mapped[int]
    tv_screen_resolution = relationship("TV", back_populates='screen_resolution', cascade='all, delete-orphan')

    def __str__(self):
        return f'<name>: {self.id} {self.name}'
