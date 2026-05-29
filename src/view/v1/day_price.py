from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import selectinload

from settings.database import get_session
from model.day_price import DayPrice
from model.shop_link import ShopLink
from model.tv import TV
from repository.day_price import DayPriceData
from schema.pagination import PaginationResponseSchema
from schema.day_price import (
    DayPriceFilterSchema,
    DayPriceFullResponseSchema,
    DayPricePostSchema,
    DayPriceUpdateSchema,
    DayPriceSmallResponseSchema,
)


router = APIRouter(prefix='/day_price', tags=['DayPrice'])


@router.get('/', response_model=PaginationResponseSchema[DayPriceFullResponseSchema])
async def day_price_list(
        pagination: DayPriceFilterSchema = Depends(),
        session=Depends(get_session)):
    """Получить список обмена валют с пагинацией и сортировкой

    параметры пагинации:
    - Страница: ?page=0
    - Количество записей на странице: ?page_size=20

    Параметры сортировки:
    - Сортировка по ID: ?sort_field=поле сортировки
      Пример сортировки по id: ?sort_field=id
    - Порядок сортировка: ?sort_order=asc (увеличение) или desc (уменьшение)

    Параметры фильтров:
    - Фильтр по id: ?id=1
    - Фильтр по shop_link_id: ?shop_link_id=1
    - Фильтр по currency_id: ?currency_id=1
    - Фильтр по price: ?price=1.0
    - Фильтр по названию: ?name=Linux
    - Точное совпадение названия: ?name=Linux
    - Название не равно: ?name_ne=Linux
    - Название содержит подстроку: ?name_icontains=Linux
    - Название начинается с: ?name_istartswith=Linux
    - Название заканчивается на: ?name_iendswith=Linux
    - Фильтр по date: ?date=2020-01-01
    - Фильтр по date (больше): ?date__gte=2020-01-01
    - Фильтр по date (меньше): ?date__lte=2020-01-01
"""
    try:
        day_price_data = DayPriceData(session)
        eager_options = [
            selectinload(DayPrice.shop_link).options(
                selectinload(ShopLink.shop),
                selectinload(ShopLink.tv).options(
                        selectinload(TV.os),
                        selectinload(TV.screen_resolution),
                        selectinload(TV.brand),
                        selectinload(TV.matrix_type),
                        selectinload(TV.category),
                    )),
            selectinload(DayPrice.currency),
        ]
        day_price_list, total = await day_price_data.get_multi(
            skip=pagination.offset,
            limit=pagination.limit,
            sort_field=pagination.sort_field,
            sort_order=pagination.sort_order,
            filters=pagination.filters,
            eager_loads=eager_options,
        )
        day_price_schemes = [DayPriceFullResponseSchema.model_validate(item) for item in day_price_list]
        pages = pagination.get_count_pages(total)
        return PaginationResponseSchema[DayPriceFullResponseSchema](
            items=day_price_schemes,
            total=total,
            page=pagination.page,
            size=pagination.page_size,
            pages=pages,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/', response_model=DayPriceSmallResponseSchema)
async def day_price_create(day_price: DayPricePostSchema, session=Depends(get_session)):
    try:
        day_price_data = DayPriceData(session)
        new_day_price = await day_price_data.create(day_price)
        return DayPriceSmallResponseSchema.model_validate(new_day_price)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch('/patch/{id}/', response_model=DayPriceSmallResponseSchema)
async def day_price_update(id: int, day_price: DayPriceUpdateSchema, session=Depends(get_session)):
    try:
        day_price_data = DayPriceData(session)
        model = await day_price_data.update(id, day_price)
        return DayPriceSmallResponseSchema.model_validate(model)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def day_price_delete(id: int, session=Depends(get_session)):
    try:
        day_price_data = DayPriceData(session)
        await day_price_data.delete(id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
