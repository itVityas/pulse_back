from typing import Optional, List, Any, Dict
from datetime import date as datetype

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, literal_column
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

    async def get_by_shop_date(
                self,
                shop_id: int,
                date
            ) -> Optional[List[DayPrice]]:
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
            tv_ids: Optional[List[int]],
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

        if tv_ids:
            slct = slct.where(
                TV.id.in_(tv_ids)
            )
        else:
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

        buf_rez2 = []
        for key, value in buf_rez.items():
            buf_rez2.append({
                'name': key,
                'coords': value
            })

        return buf_rez2

    async def get_min_price_main_chart(
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
    ) -> list:
        slct = select(
            func.min(DayPrice.price),
            DayPrice.name,
            Shop.name,
        ).join(
            DayPrice.shop_link
        ).join(
            ShopLink.tv
        ).join(
            ShopLink.shop
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
            DayPrice.name,
            Shop.name,
        )
        result = await self.session.execute(slct)
        res_list = result.all()

        min_price = None
        min_price_disc = None
        for rez in res_list:
            if not min_price:
                min_price = rez
            else:
                if min_price[0] > rez[0]:
                    min_price = rez
            if rez[1] == 'discount_price':
                if min_price_disc:
                    if min_price_disc[0] > rez[0]:
                        min_price_disc = rez
                else:
                    min_price_disc = rez

        change_persent = await self.get_change_price(
            date_start, date_end, diag_min, diag_max,
            shops, brands, os, screen_resolutions,
            matrix_type, refresh_rate, currency
        )

        min_price_dict = {}
        if min_price:
            min_price_dict['shop'] = min_price[2]
            min_price_dict['price'] = min_price[0]
            min_price_dict['name'] = min_price[1]

        min_price_disc_dict = {}
        if min_price_disc:
            min_price_disc_dict['shop'] = min_price_disc[2]
            min_price_disc_dict['price'] = min_price_disc[0]
            min_price_disc_dict['name'] = min_price_disc[1]

        return {
                "min_price": min_price_dict,
                "min_price_disc": min_price_disc_dict,
                "change_percent": change_persent
            }

    async def get_change_price(
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
    ):
        slct = select(
            DayPrice
        ).join(
            DayPrice.shop_link
        ).join(
            ShopLink.tv
        ).join(
            ShopLink.shop
        ).where(
            DayPrice.date >= date_start,
            DayPrice.date <= date_end,
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

        f_prices = slct.cte('filtered_prices')

        dates_subq = select(
            func.min(f_prices.c.date).label('min_d'),
            func.max(f_prices.c.date).label('max_d')
        ).subquery()

        final_slct = select(
            func.min(
                case(
                    (f_prices.c.date == dates_subq.c.min_d, f_prices.c.price)
                )
            ).label('price_start'),
            func.min(
                case(
                    (f_prices.c.date == dates_subq.c.max_d, f_prices.c.price)
                )
            ).label('price_end')
        ).select_from(
            f_prices
        ).join(
            dates_subq, literal_column('true')
        )

        result = await self.session.execute(final_slct)
        rez = result.fetchone()

        if len(rez) == 2:
            change = ((rez[1] - rez[0]) / rez[0]) * 100
            return change

    async def get_models_min_price(
        self,
            date_start: datetype, date_end: datetype,
            diag_min: Optional[int], diag_max: Optional[int],
            shops: Optional[List[int]],
            brands: Optional[List[int]],
            os: Optional[List[int]],
            screen_resolutions: Optional[List[int]],
            matrix_type: Optional[List[int]],
            refresh_rate: Optional[List[int]],
            currency: str,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[Dict[str, Any]] = None,
    ) -> Optional[dict]:
        # need to handle currency
        slct = select(
            func.min(DayPrice.price),
            Shop.name,
            TV.name,
            ShopLink.link,
            TV.id
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
            Shop.name,
            TV.name,
            ShopLink.link,
            TV.id
        ).order_by(
            TV.name
        )

        if filters:
            for field, value in filters.items():
                if '__' in field and value is not None:
                    field, operator = field.split('__')
                    if field == 'name':
                        if operator == 'eq':
                            slct = slct.having(func.lower(TV.name) == func.lower(value))
                        if operator == 'ne':
                            slct = slct.having(func.lower(TV.name) != func.lower(value))
                        if operator == 'icontains':
                            slct = slct.having(func.lower(TV.name).contains(func.lower(value)))
                        if operator == 'istartswith':
                            slct = slct.having(func.lower(TV.name).startswith(func.lower(value)))
                        if operator == 'iendswith':
                            slct = slct.having(func.lower(TV.name).endswith(func.lower(value)))

        count_query = select(func.count()).select_from(slct)
        count_res = await self.session.execute(count_query)
        total = count_res.scalar_one()

        if limit != -1:
            slct = slct.offset(skip).limit(limit)

        result = await self.session.execute(slct)
        res_list = result.all()

        rez = dict()
        for i in res_list:
            if not rez.get(i[4]):
                rez[i[4]] = []
            rez[i[4]].append({
                'price': i[0],
                'name': i[2],
                'shop': i[1],
                'link': i[3],
                'tv_id': i[4]
            })

        return rez, total
