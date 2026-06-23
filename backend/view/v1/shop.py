from fastapi import APIRouter, Depends, status

from settings.database import get_session
from repository.shop import ShopData
from schema.pagination import PaginationResponseSchema
from schema.shop import (
    ShopFullSchema,
    ShopParamsFilterSchema,
    ShopSmallSchema,
    ShopUpdateShema,
)
from share.my_exception import MyHttpException


router = APIRouter(prefix='/shops', tags=['Shops'])


@router.get('/', response_model=PaginationResponseSchema[ShopFullSchema])
async def shops_get(
        pagination: ShopParamsFilterSchema = Depends(),
        session=Depends(get_session)
):
    """Получить список магазинов с пагинацией, сортировкой и фильтрацией

    параметры пагинации:
    - Страница: ?page=0
    - Количество записей на странице: ?page_size=20

    Параметры сортировки:
    - Сортировка по ID: ?sort_field=поле сортировки
      Пример сортировки по id: ?sort_field=id
    - Порядок сортировка: ?sort_order=asc (увеличение) или desc (уменьшение)

    Параметры фильтров:
    - Фильтр по id: ?id=1
    - Фильтр по названию: ?name=Linux
    - Точное совпадение названия: ?name=Linux
    - Название не равно: ?name_ne=Linux
    - Название содержит подстроку: ?name_icontains=Linux
    - Название начинается с: ?name_istartswith=Linux
    - Название заканчивается на: ?name_iendswith=Linux
    - URL магазина: ?url=https://www.ozon.ru/
    """
    try:
        shop_data = ShopData(session)
        shops, total = await shop_data.get_multi(
            limit=pagination.limit,
            skip=pagination.offset,
            filters=pagination.filters,
            sort_field=pagination.sort_field,
            sort_order=pagination.sort_order,
        )
        shop_schemes = [ShopFullSchema.model_validate(shop) for shop in shops]
        pages = pagination.get_count_pages(total)
        return PaginationResponseSchema[ShopFullSchema](
            items=shop_schemes,
            total=total,
            page=pagination.page,
            size=pagination.page_size,
            pages=pages
        )
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )


@router.post('/', response_model=ShopSmallSchema)
async def shop_create(shop: ShopSmallSchema, session=Depends(get_session)):
    try:
        shop_data = ShopData(session)
        new_shop = await shop_data.create(shop)
        return ShopSmallSchema.model_validate(new_shop)
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )


@router.patch('/patch/{id}/', response_model=ShopSmallSchema)
async def shop_update(
            id: int,
            shop: ShopUpdateShema,
            session=Depends(get_session)
        ):
    try:
        shop_data = ShopData(session)
        model = await shop_data.update(id, shop)
        return ShopSmallSchema.model_validate(model)
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )


@router.delete('/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def shop_delete(id: int, session=Depends(get_session)):
    try:
        shop_data = ShopData(session)
        await shop_data.delete(id)
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )
