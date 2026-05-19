from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from model.os import OS
from repository.base import BaseData


class OSData(BaseData):
    def __init__(self, model: OS, session: AsyncSession):
        super().__init__(model=model, session=session)

    async def get_by_name(self, name: str) -> OS:
        statement = select(OS).where(OS.name == name)
        result = await self.session.execute(statement)
        return result.scalars().first()
