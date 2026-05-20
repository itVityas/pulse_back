from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from model.matrix_type import MatrixType
from repository.base import BaseData


class MatrixTypeData(BaseData):
    def __init__(self, session: AsyncSession, model: MatrixType = MatrixType):
        super().__init__(model=MatrixType, session=session)

    async def get_by_name(self, name: str):
        slct = select(self.model).where(self.model.name == name)
        result = await self.session.execute(slct)
        return result.scalars().first()
