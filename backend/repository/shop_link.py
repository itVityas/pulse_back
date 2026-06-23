from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from model.shop_link import ShopLink
from repository.base import BaseData


class ShopLinkData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(model=ShopLink, session=session)

    async def get_by_shop_tv(self, shop_id: int, tv_id: int):
        stmt = select(ShopLink).where(
            ShopLink.shop_id == shop_id,
            ShopLink.tv_id == tv_id,
            ShopLink.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalars().first()
