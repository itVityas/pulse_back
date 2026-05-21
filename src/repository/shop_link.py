from sqlalchemy.ext.asyncio import AsyncSession

from model.shop_link import ShopLink
from repository.base import BaseData


class ShopLinkData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(model=ShopLink, session=session)
