from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from model.day_price import DayPrice
from model.shop_link import ShopLink
from repository.base import BaseData


class DayPriceData(BaseData):
    def __init__(self, session: AsyncSession, model: DayPrice = DayPrice):
        super().__init__(model=DayPrice, session=session)

    async def get_by_shop_date(self, shop_id: int, date):
        slct = select(self.model).join(
                self.model.shop_link
            ).options(
                selectinload(DayPrice.shop_link)
            ).where(
                ShopLink.shop_id == shop_id,
                self.model.date == date
            )
        result = await self.session.execute(slct)
        return result.scalars().all()
