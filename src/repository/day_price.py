from datetime import date
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from model.day_price import DayPrice
from model.shop_link import ShopLink
from model.shop import Shop
from repository.base import BaseData


class DayPriceData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(model=DayPrice, session=session)

    async def get_by_shop_date(self, shop_id: int, date) -> Optional[List[DayPrice]]:
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

    async def get_for_main_chart(
            self,
            date_start: date, date_end: date,
            diag_min: Optional[int], diag_max: Optional[int],
            shops: Optional[List[int]],
            brands: Optional[List[int]],
            os: Optional[List[int]],
            screen_resolutions: Optional[List[int]],
            matrix_type: Optional[List[int]],
            refresh_rate: Optional[List[int]],
            currency: str
    ) -> Optional[List[DayPrice]]:
        # need to handle currency
        slct = select(self.model).where(
            DayPrice.date >= date_start,
            DayPrice.date <= date_end)
        if shops:
            slct = slct.join(
                    DayPrice.shop_link
                ).join(
                    ShopLink.shop
                ).where(
                    Shop.name.in_(shops)
                )
        result = await self.session.execute(slct)
        return result.scalars().all()
