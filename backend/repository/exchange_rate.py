from datetime import date as datetype

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from model.exchange_rate import ExchangeRate
from repository.base import BaseData


class ExchangeRateData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(model=ExchangeRate, session=session)

    async def check_exist(self, date: datetype, currency_id: int = None) -> bool:
        if currency_id:
            query = select(select(ExchangeRate).where(
                (ExchangeRate.currency_id == currency_id) &
                (ExchangeRate.date == date)
            ).exists())
        else:
            query = select(select(ExchangeRate).where(
                ExchangeRate.date == date
            ).exists())
        is_exist = await self.session.scalar(query)
        return is_exist
