from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from model.tv import TV
from repository.base import BaseData


class TVData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(model=TV, session=session)

    async def get_by_name(self, name: str):
        stmt = select(TV).where(TV.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()
