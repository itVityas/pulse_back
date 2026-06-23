from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class User(BaseModel):
    """Модель пользователя: id, username, password, is_active, created_at, updated_at
    """
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __str__(self):
        return f'<user>: {self.id} {self.username}'
