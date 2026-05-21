from fastapi import APIRouter, Depends, status, HTTPException

from settings.database import get_session
from model.tv import TV
from repository.tv import TVData
from schema.pagination import PaginationResponseSchema
from schema.tv import (
    TVFilterSchema,
    TVFullResponceSchema,
    TVPOSTSchema,
    TVSmallResponseSchema,
    TVUpdateSchema,
)


router = APIRouter(prefix='/tv', tags=['TV'])


@router.get('/', response_model=PaginationResponseSchema[TVFullResponceSchema])
async def tv_list(pagination: TVFilterSchema = Depends(), session=Depends(get_session)):
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
    - Фильтр по названию: ?name=Samsung
    - Фильтр по названию (не равно): ?name__ne=Samsung
    - Фильтр по названию (содержит): ?name__icontains=Samsung
    - Фильтр по названию (начинается с): ?name__istartswith=Samsung
    - Фильтр по названию (заканчивается на): ?name__iendswith=Samsung
    - Фильтр по id ОС: ?os_id=1
    - Фильтр по id разрешения экрана: ?screen_resolution_id=1
    - Фильтр по id бренда: ?brand_id=1
    - Фильтр по id типа матрицы: ?matrix_type_id=1
    - Фильтр по цвету: ?color=black
    - Фильтр по частоте обновления: ?refresh_rate=60
    - Фильтр по диагонали: ?diagonal=32
    """
    try:
        tv_data = TVData(TV, session)
        tv_list, total = await tv_data.get_multi(
            skip=pagination.offset,
            limit=pagination.limit,
            sort_field=pagination.sort_field,
            sort_order=pagination.sort_order,
            filters=pagination.filters,
            eager_loads=[
                'os',
                'screen_resolution',
                'brand',
                'matrix_type',]
        )
        tv_schemes = [TVFullResponceSchema.model_validate(item) for item in tv_list]
        pages = pagination.get_count_pages(total)
        return PaginationResponseSchema[TVFullResponceSchema](
            items=tv_schemes,
            total=total,
            page=pagination.page,
            size=pagination.page_size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/', response_model=TVSmallResponseSchema)
async def tv_create(tv: TVPOSTSchema, session=Depends(get_session)):
    try:
        tv_data = TVData(TV, session)
        new_tv = await tv_data.create(tv)
        return TVSmallResponseSchema.model_validate(new_tv)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch('/patch/{id}/', response_model=TVSmallResponseSchema)
async def tv_update(id: int, tv: TVUpdateSchema, session=Depends(get_session)):
    try:
        tv_data = TVData(TV, session)
        model = await tv_data.update(id, tv)
        return TVSmallResponseSchema.model_validate(model)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def tv_delete(id: int, session=Depends(get_session)):
    try:
        tv_data = TVData(TV, session)
        await tv_data.delete(id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
