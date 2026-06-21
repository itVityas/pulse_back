from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(insert_default=func.now(), nullable=False, onupdate=func.now())


class BaseModel(Base, TimestampMixin):
    """Base model: id, created_at, updated_at
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)


class BaseModelOnlyId(Base):
    """Base model: id
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
