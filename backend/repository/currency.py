from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from model.currency import Currency
from repository.base import BaseData


class CurrencyData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Currency, session=session)

    async def get_by_name(self, name: str):
        stmt = select(self.model).where(self.model.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()
