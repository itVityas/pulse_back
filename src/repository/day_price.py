from typing import Optional, List
from datetime import date as datetype

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from model.tv import TV
from repository.base import BaseData
from model.shop import Shop
from model.day_price import DayPrice
from model.shop_link import ShopLink
from model.brand import Brand
from model.os import OS
from model.matrix_type import MatrixType
from model.screen_resolution import ScreenResolution


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
            date_start: datetype, date_end: datetype,
            diag_min: Optional[int], diag_max: Optional[int],
            shops: Optional[List[int]],
            brands: Optional[List[int]],
            os: Optional[List[int]],
            screen_resolutions: Optional[List[int]],
            matrix_type: Optional[List[int]],
            refresh_rate: Optional[List[int]],
            currency: str
    ) -> Optional[List]:
        # need to handle currency
        slct = select(
            func.min(DayPrice.price),
            DayPrice.date,
            Shop.name,
        ).join(
            DayPrice.shop_link
        ).join(
            ShopLink.shop
        ).join(
            ShopLink.tv
        ).where(
            DayPrice.date >= date_start,
            DayPrice.date <= date_end
        )

        if shops:
            slct = slct.where(
                Shop.name.in_(shops)
            )
        if brands:
            slct = slct.join(
                    TV.brand
                ).where(
                    Brand.name.in_(brands)
                )
        if matrix_type:
            slct = slct.join(
                TV.matrix_type
            ).where(
                MatrixType.name.in_(matrix_type)
            )
        if os:
            slct = slct.join(
                TV.os
            ).where(
                OS.name.in_(os)
            )
        if screen_resolutions:
            slct = slct.join(
                TV.screen_resolution
            ).where(
                ScreenResolution.name.in_(screen_resolutions)
            )
        if refresh_rate:
            slct = slct.where(
                TV.refresh_rate.in_(refresh_rate)
            )
        if diag_min:
            slct = slct.where(
                TV.diagonal >= diag_min
            )
        if diag_max:
            slct = slct.where(
                TV.diagonal <= diag_max
            )
        slct = slct.group_by(
            DayPrice.date,
            Shop.name,
        )
        result = await self.session.execute(slct)
        res_list = result.all()

        buf_rez = {}
        for line in res_list:
            min_obj = buf_rez.get(line[2])
            if min_obj:
                min_obj.append([str(line[1]), line[0]])
            else:
                buf_rez[line[2]] = [(str(line[1]), line[0]),]

        return buf_rez
