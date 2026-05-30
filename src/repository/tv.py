from datetime import date
from typing import Optional, List

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


class TVData(BaseData):
    def __init__(self, session: AsyncSession):
        super().__init__(model=TV, session=session)

    async def get_by_name(self, name: str):
        stmt = select(TV).where(TV.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()

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
    ) -> Optional[List]:
        # need to handle currency
        slct = select(TV).join(
            TV.tv_shop_link
        ).join(
            ShopLink.price_shop_link
        ).where(
            DayPrice.date >= date_start,
            DayPrice.date <= date_end
        )
        slct = slct.options(
            selectinload(
                TV.tv_shop_link
            ).options(
                selectinload(ShopLink.price_shop_link),
                selectinload(ShopLink.shop),
            ))
        if shops:
            slct = slct.join(
                    ShopLink.shop
                ).where(
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
        result = await self.session.execute(slct)
        tv_list = result.scalars().all()

        rez_list = {}
        for tv in tv_list:
            for shop_link in tv.tv_shop_link:
                for day_price in shop_link.price_shop_link:
                    buf_date = rez_list.get(day_price.date)
                    min_price = day_price.price
                    if buf_date:
                        shop = buf_date.get(shop_link.shop.name)
                        if shop:
                            if min_price < shop['min_price']:
                                shop['min_price'] = min_price
                                shop['tv'] = tv.name
                                shop['tv_link'] = shop_link.link
                        else:
                            buf_date[shop_link.shop.name] = {
                                    'min_price': min_price,
                                    'tv': tv.name,
                                    'tv_link': shop_link.link
                                }
                    else:
                        rez_list[day_price.date] = {
                            shop_link.shop.name: {
                                'min_price': min_price,
                                'tv': tv.name,
                                'tv_link': shop_link.link
                            }
                        }
        return rez_list
