from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from model.screen_resolution import ScreenResolution
from repository.base import BaseData


class ScreenResolutionData(BaseData):
    def __init__(self, model: ScreenResolution, session: AsyncSession):
        super().__init__(
            model=model, session=session
        )

    async def get_by_name(self, name: str):
        slct = select(self.model).where(self.model.name == name)
        result = await self.session.execute(slct)
        return result.scalars().first()
