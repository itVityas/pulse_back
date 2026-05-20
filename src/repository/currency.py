from sqlalchemy.ext.asyncio import AsyncSession

from model.currency import Currency
from repository.base import BaseData


class CurrencyData(BaseData):
    def __init__(self, session: AsyncSession, model: Currency = Currency):
        super().__init__(model=Currency, session=session)
