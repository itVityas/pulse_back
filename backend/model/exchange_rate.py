from datetime import date as datetype
from decimal import Decimal

from sqlalchemy import func, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelOnlyId


class ExchangeRate(BaseModelOnlyId):
    """Модель для курса валют: id, currency_id, rate, date, base_currensy_id
    currency_id: валюта
    base_currency_id: базовая валюта к которой приводится курс
    """
    __tablename__ = 'exchange_rate'

    date: Mapped[datetype] = mapped_column(
        insert_default=func.current_date(),
        nullable=False,
        index=True)
    currency_id: Mapped[int] = mapped_column(
        ForeignKey('currency.id'),
        nullable=False,
        index=True)
    currency = relationship("Currency", foreign_keys=currency_id)
    base_currency_id: Mapped[int] = mapped_column(
        ForeignKey('currency.id'),
        nullable=False,
        index=True)
    base_currency = relationship("Currency", foreign_keys=base_currency_id)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    scale: Mapped[int] = mapped_column(nullable=False, server_default='1')

    __table_args__ = (
        UniqueConstraint("date", "currency_id", 'base_currency_id', name="uq_date_currency"),
    )

    def __str__(self):
        return f'<Currency>: {self.id}'
