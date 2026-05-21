from fastapi import APIRouter, Depends, status, HTTPException

from settings.database import get_session
from repository.brand import BrandData
from schema.pagination import PaginationResponseSchema
from schema.brand import (
    BrandFullSchema,
    BrandPaginationParamsSchema,
    BrandSmallSchema,
    BrandUpdateSchema,
)

router = APIRouter(prefix='/brand', tags=['Brand'])


@router.get('/', response_model=PaginationResponseSchema[BrandFullSchema])
async def brand_list(
                        pagination: BrandPaginationParamsSchema = Depends(),
                        session=Depends(get_session),
                    ):
    """Получить список брендов с пагинацией и сортировкой

    параметры пагинации:
    - Страница: ?page=0
    - Количество записей на странице: ?page_size=20

    Параметры сортировки:
    - Сортировка по ID: ?sort_field=поле сортировки
      Пример сортировки по id: ?sort_field=id
    - Порядок сортировка: ?sort_order=asc (увеличение) или desc (уменьшение)

    Параметры фильтров:
    - Фильтр по id: ?id=1
    - Фильтр по названию: ?name=ASUS
    - Точное совпадение названия: ?name=ASUS
    - Название не равно: ?name_ne=ASUS
    - Название содержит подстроку: ?name_icontains=ASUS
    - Название начинается с: ?name_istartswith=ASUS
    - Название заканчивается на: ?name_iendswith=ASUS
    - Фильтр по стране: ?country=China
    - Точное совпадение страны: ?country=China
    - Страна не равна: ?country_ne=China
    - Страна содержит подстроку: ?country_icontains=China
    - Страна начинается с: ?country_istartswith=China
    - Страна заканчивается на: ?country_iendswith=China
    """
    try:
        brand_model = BrandData(session)
        brand_list, total = await brand_model.get_multi(
            skip=pagination.offset,
            limit=pagination.limit,
            sort_field=pagination.sort_field,
            sort_order=pagination.sort_order,
            filters=pagination.filters,
        )
        pages = pagination.get_count_pages(total)
        return PaginationResponseSchema[BrandFullSchema](
            items=brand_list,
            total=total,
            page=pagination.page,
            size=pagination.page_size,
            pages=pages,)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/', response_model=BrandFullSchema)
async def brand_create(brand: BrandSmallSchema, session=Depends(get_session)):
    try:
        brand_data = BrandData(session)
        new_brand = await brand_data.create(brand)
        return BrandFullSchema.model_validate(new_brand)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch('/patch/{id}/', response_model=BrandFullSchema)
async def brand_update(id: int, brand: BrandUpdateSchema, session=Depends(get_session)):
    try:
        brand_data = BrandData(session)
        model = await brand_data.update(id, brand)
        return BrandFullSchema.model_validate(model)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def brand_delete(id: int, session=Depends(get_session)):
    try:
        brand_data = BrandData(session)
        await brand_data.delete(id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
