from sqlalchemy.ext.asyncio import AsyncSession

from model.tv import TV
from repository.base import BaseData


class TVData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(model=TV, session=session)
