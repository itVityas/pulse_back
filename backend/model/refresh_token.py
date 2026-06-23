from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, func, ForeignKey

from .base import BaseModelOnlyId


class RefreshToken(BaseModelOnlyId):
    __tablename__ = 'refresh_token'

    token: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    revoked: Mapped[bool] = mapped_column(default=False)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    user_id: Mapped[id] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    def __str__(self):
        return f'<Currency>: {self.id}'
