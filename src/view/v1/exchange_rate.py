from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import selectinload

from model.exchange_rate import ExchangeRate
from schema.exchange_rate import (
    ExchangeRateFullSchema,
    ExchangeRateParamsSchema,
    ExchangeRateSmallSchema,
    ExchangeRateSimpleSchema,
    ExchangeRatePatchSchema,
    UploadCurrencySchema,
)
from schema.pagination import PaginationResponseSchema
from repository.exchange_rate import ExchangeRateData
from settings.database import get_session
from service.currency_upload import get_currency_from_nbrb


router = APIRouter(prefix='/exchange_rate', tags=['ExchangeRate'])


@router.get('/', response_model=PaginationResponseSchema[ExchangeRateFullSchema])
async def exchange_rate_list(
                                pagination=Depends(ExchangeRateParamsSchema),
                                session=Depends(get_session),
                            ):
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
    - Фильтр по точной дате: ?date=2026-05-09
    - Фильтр для даты больше: date_gte=2026-05-09
    - Фильтр для даты меньше: date_lte=2026-05-09
    - Фильтр для id валюты: currency_id=2
    - Фильтр для id валюты к которой обмениваем: base_currency_id=3
    """
    try:
        exchage_rate_model = ExchangeRateData(session)
        eager_options = [selectinload(ExchangeRate.currency), selectinload(ExchangeRate.base_currency)]
        exchage_rate_list, total = await exchage_rate_model.get_multi(
            skip=pagination.offset,
            limit=pagination.limit,
            sort_field=pagination.sort_field,
            sort_order=pagination.sort_order,
            filters=pagination.filters,
            eager_loads=eager_options
        )
        exchange_rate_schemes = [ExchangeRateFullSchema.model_validate(item) for item in exchage_rate_list]
        pages = pagination.get_count_pages(total)
        return PaginationResponseSchema[ExchangeRateFullSchema](
            items=exchange_rate_schemes,
            total=total,
            page=pagination.page,
            size=pagination.page_size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/', response_model=ExchangeRateSimpleSchema)
async def exchange_rate_create(exchange_rate: ExchangeRateSmallSchema, session=Depends(get_session)):
    try:
        exchange_rate_data = ExchangeRateData(session)
        new_exchange_rate = await exchange_rate_data.create(exchange_rate)
        return ExchangeRateSimpleSchema.model_validate(new_exchange_rate)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def exchange_rate_delete(id: int, session=Depends(get_session)):
    try:
        exchange_rate_data = ExchangeRateData(session)
        await exchange_rate_data.delete(id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch('/patch/{id}/', response_model=ExchangeRateSimpleSchema)
async def exchange_rate_patch(id: int, exchange_rate: ExchangeRatePatchSchema, session=Depends(get_session)):
    try:
        exchange_rate_data = ExchangeRateData(session)
        model = await exchange_rate_data.update(id, exchange_rate)
        return ExchangeRateSimpleSchema.model_validate(model)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/upload/', status_code=status.HTTP_201_CREATED)
async def currency_upload(upload_data: UploadCurrencySchema, session=Depends(get_session)):
    """upload currency from nbrb
    date: date witch upload
    """
    try:
        await get_currency_from_nbrb(session, upload_data.date)
        return {'status': 'created'}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
