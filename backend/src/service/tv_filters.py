from typing import Optional, List
from datetime import date as datetype

from model.tv import TV
from model.shop import Shop
from model.day_price import DayPrice
from model.brand import Brand
from model.os import OS
from model.matrix_type import MatrixType
from model.screen_resolution import ScreenResolution


async def apply_tv_filters(
            query,
            date_start: datetype,
            date_end: datetype,
            diag_min: Optional[int],
            diag_max: Optional[int],
            shops: Optional[List[str]],
            brands: Optional[List[str]],
            os: Optional[List[str]],
            screen_resolutions: Optional[List[str]],
            matrix_type: Optional[List[str]],
            refresh_rate: Optional[List[int]],
            tv_ids: Optional[List[int]],
            currency: str
        ):
    """apply filters to DayPrice query. Need join ShopLink, Shop, TV

    Args:
        query (_type_): select
        date_start (datetype)
        date_end (datetype)
        diag_min (Optional[int])
        diag_max (Optional[int])
        shops (Optional[List[str]])
        brands (Optional[List[str]])
        os (Optional[List[str]])
        screen_resolutions (Optional[List[str]])
        matrix_type (Optional[List[str]])
        refresh_rate (Optional[List[int]])
        tv_ids (Optional[List[int]])
        currency (str)

    Returns:
        query
    """
    if date_start and date_end:
        query = query.where(
            DayPrice.date >= date_start,
            DayPrice.date <= date_end
        )

    if tv_ids:
        query = query.where(
            TV.id.in_(tv_ids)
        )
        return query
    else:
        if shops:
            query = query.where(
                Shop.name.in_(shops)
            )
        if brands:
            query = query.join(
                    TV.brand
                ).where(
                    Brand.name.in_(brands)
                )
        if matrix_type:
            query = query.join(
                TV.matrix_type
            ).where(
                MatrixType.name.in_(matrix_type)
            )
        if os:
            query = query.join(
                TV.os
            ).where(
                OS.name.in_(os)
            )
        if screen_resolutions:
            query = query.join(
                TV.screen_resolution
            ).where(
                ScreenResolution.name.in_(screen_resolutions)
            )
        if refresh_rate:
            query = query.where(
                TV.refresh_rate.in_(refresh_rate)
            )
        if diag_min:
            query = query.where(
                TV.diagonal >= diag_min
            )
        if diag_max:
            query = query.where(
                TV.diagonal <= diag_max
            )
    return query
