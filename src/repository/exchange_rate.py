from sqlalchemy.ext.asyncio import AsyncSession

from model.exchange_rate import ExchangeRate
from repository.base import BaseData


class ExchangeRateData(BaseData):
    def __init__(
                    self, session: AsyncSession,
                    model: ExchangeRate = ExchangeRate):
        super().__init__(model=ExchangeRate, session=session)
