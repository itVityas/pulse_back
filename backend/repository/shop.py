from sqlalchemy.ext.asyncio import AsyncSession

from model.shop import Shop
from repository.base import BaseData


class ShopData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(Shop, session)
