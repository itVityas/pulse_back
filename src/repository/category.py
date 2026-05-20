from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from model.category import Category
from .base import BaseData


class CategoryData(BaseData):
    def __init__(self, session: AsyncSession, model: Category = Category):
        super().__init__(
            model=Category, session=session
        )

    async def get_by_name(self, name: str):
        slct = select(self.model).where(self.model.name == name)
        result = await self.session.execute(slct)
        return result.scalars().first()
