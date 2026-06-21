from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, literal

from model.brand import Brand
from repository.base import BaseData


class BrandData(BaseData):
    def __init__(self, session: AsyncSession,):
        super().__init__(model=Brand, session=session)

    async def get_by_name(self, name: str):
        slct = select(self.model).where(self.model.name.ilike(name))
        result = await self.session.execute(slct)
        return result.scalars().first()

    async def get_by_entry(self, tv_name: str) -> Brand:
        slct = select(Brand).where(literal(tv_name).contains(Brand.name))
        result = await self.session.execute(slct)
        return result.scalars().first()
