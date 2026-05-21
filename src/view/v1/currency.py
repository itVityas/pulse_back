from fastapi import APIRouter, Depends, HTTPException, status

from schema.currency import (CurrencyFullSchema, CurrencySmallSchema, CurrencyPaginationParamsSchema)
from repository.currency import CurrencyData
from settings.database import get_session
from schema.pagination import PaginationResponseSchema


router = APIRouter(prefix='/currency', tags=['Currency'])


@router.get('/', response_model=PaginationResponseSchema[CurrencyFullSchema])
async def currency_list(
                pagination: CurrencyPaginationParamsSchema = Depends(),
                session=Depends(get_session)):
    """Получить список валют с пагинацией и сортировкой

    параметры пагинации:
    - Страница: ?page=0
    - Количество записей на странице: ?page_size=20

    Параметры сортировки:
    - Сортировка по ID: ?sort_field=id
    - Сортировка по username: ?sort_field=name
    - Обратная сортировка: ?sort_order=asc или desc

    Параметры фильтров:
    - Фильтр по id: ?id=1
    - Фильтр по названию: ?name=USD
    - Фильтр по части назвалния: ?name__icontains=USD
    - Фильтр по началу названия: ?name__istartswith=US
    - Фильтр по окончанию названия: ?name__iendswith=D
    """
    try:
        currency_model = CurrencyData(session)
        currencies, total = await currency_model.get_multi(
            skip=pagination.offset,
            limit=pagination.limit,
            sort_field=pagination.sort_field,
            sort_order=pagination.sort_order,
            filters=pagination.filters)
        currencies_schema = [CurrencyFullSchema.model_validate(currency) for currency in currencies]
        pages = total // pagination.page_size + (1 if total % pagination.page_size else 0)
        return PaginationResponseSchema[CurrencyFullSchema](
            items=currencies_schema,
            total=total,
            page=pagination.page,
            size=pagination.page_size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/', response_model=CurrencyFullSchema, status_code=status.HTTP_201_CREATED)
async def currency_create(currency: CurrencySmallSchema, session=Depends(get_session)):
    try:
        currency_data = CurrencyData(session)
        new_currency = await currency_data.create(currency)
        return CurrencyFullSchema.model_validate(new_currency)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put('/update/{id}/', response_model=CurrencyFullSchema)
async def currency_change(id: int, currensy: CurrencySmallSchema, session=Depends(get_session)):
    try:
        currency_data = CurrencyData(session)
        model = await currency_data.update(id, currensy)
        return CurrencyFullSchema.model_validate(model)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def currency_delete(id: int, session=Depends(get_session)):
    try:
        currency_data = CurrencyData(session)
        await currency_data.delete(id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
