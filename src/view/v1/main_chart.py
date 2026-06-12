from fastapi import APIRouter, status, Depends

from share.my_exception import MyHttpException
from settings.database import get_session
from schema.main_chart import (
    MainChartRequestSchema,
    MainChartTVMinPriceResponse,
    MainChartValuesTVMinPrice,
    MainChartTVMinPriceRequestPaginationSortSchema)
from repository.day_price import DayPriceData
from schema.pagination import PaginationResponseSchema


router = APIRouter(prefix='/chart', tags=['Chart'],)


@router.post('/main_chart/', status_code=status.HTTP_200_OK)
async def get_main_chart(
            chart: MainChartRequestSchema,
            session=Depends(get_session)
        ):
    try:
        shops = None
        brands = None
        os = None
        screen_resolutions = None
        matrix_types = None
        refresh_rate = None
        currency = None
        diag_min = None
        diag_max = None
        tv_ids = None
        for item in chart.root:
            if item.field == "date_range":
                date_start = item.data.start
                date_end = item.data.end
            elif item.field == "diagonal":
                diag_min = item.data.min
                diag_max = item.data.max
            elif item.field == 'shops':
                shops = item.data
            elif item.field == 'brands':
                brands = item.data
            elif item.field == 'os':
                os = item.data
            elif item.field == 'screen_resolutions':
                screen_resolutions = item.data
            elif item.field == 'matrix_types':
                matrix_types = item.data
            elif item.field == 'refresh_rate':
                refresh_rate = item.data
            elif item.field == 'currency':
                currency = item.data
            elif item.field == 'tv_ids':
                tv_ids = item.data

        results = await DayPriceData(session=session).get_for_main_chart(
            date_start=date_start,
            date_end=date_end,
            diag_min=diag_min,
            diag_max=diag_max,
            shops=shops,
            brands=brands,
            os=os,
            screen_resolutions=screen_resolutions,
            matrix_type=matrix_types,
            refresh_rate=refresh_rate,
            tv_ids=tv_ids,
            currency=currency
        )

        return results
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )


@router.post('/min_price/', status_code=status.HTTP_200_OK)
async def get_min_price(
            chart: MainChartRequestSchema,
            session=Depends(get_session)
        ):
    try:
        shops = None
        brands = None
        os = None
        screen_resolutions = None
        matrix_types = None
        refresh_rate = None
        currency = None
        diag_min = None
        diag_max = None
        for item in chart.root:
            if item.field == "date_range":
                date_start = item.data.start
                date_end = item.data.end
            elif item.field == "diagonal":
                diag_min = item.data.min
                diag_max = item.data.max
            elif item.field == 'shops':
                shops = item.data
            elif item.field == 'brands':
                brands = item.data
            elif item.field == 'os':
                os = item.data
            elif item.field == 'screen_resolutions':
                screen_resolutions = item.data
            elif item.field == 'matrix_types':
                matrix_types = item.data
            elif item.field == 'refresh_rate':
                refresh_rate = item.data
            elif item.field == 'currency':
                currency = item.data

        results = await DayPriceData(session=session).get_min_price_main_chart(
            date_start=date_start,
            date_end=date_end,
            diag_min=diag_min,
            diag_max=diag_max,
            shops=shops,
            brands=brands,
            os=os,
            screen_resolutions=screen_resolutions,
            matrix_type=matrix_types,
            refresh_rate=refresh_rate,
            currency=currency
        )
        return results
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )


@router.post('/models_price/',
             status_code=200,
             response_model=PaginationResponseSchema[MainChartTVMinPriceResponse])
async def get_models_min_price(
            chart: MainChartTVMinPriceRequestPaginationSortSchema,
            session=Depends(get_session),
        ):
    """
    Параметры фильтров:
    - Фильтр по id: ?id=1
    - Фильтр по названию: ?name__eq=Samsung
    - Фильтр по названию (не равно): ?name__ne=Samsung
    - Фильтр по названию (содержит): ?name__icontains=Samsung
    - Фильтр по названию (начинается с): ?name__istartswith=Samsung
    - Фильтр по названию (заканчивается на): ?name__iendswith=Samsung
    """
    try:
        shops = None
        brands = None
        os = None
        screen_resolutions = None
        matrix_types = None
        refresh_rate = None
        currency = None
        diag_min = None
        diag_max = None
        for item in chart.root:
            if item.field == "date_range":
                date_start = item.data.start
                date_end = item.data.end
            elif item.field == "diagonal":
                diag_min = item.data.min
                diag_max = item.data.max
            elif item.field == 'shops':
                shops = item.data
            elif item.field == 'brands':
                brands = item.data
            elif item.field == 'os':
                os = item.data
            elif item.field == 'screen_resolutions':
                screen_resolutions = item.data
            elif item.field == 'matrix_types':
                matrix_types = item.data
            elif item.field == 'refresh_rate':
                refresh_rate = item.data
            elif item.field == 'currency':
                currency = item.data

        results, total = await DayPriceData(session=session).get_models_min_price(
            date_start=date_start,
            date_end=date_end,
            diag_min=diag_min,
            diag_max=diag_max,
            shops=shops,
            brands=brands,
            os=os,
            screen_resolutions=screen_resolutions,
            matrix_type=matrix_types,
            refresh_rate=refresh_rate,
            currency=currency,
            skip=chart.offset,
            limit=chart.limit,
            filters=chart.filters,
        )
        res_schema = list()
        for key, items in results.items():
            res_schema.append(MainChartTVMinPriceResponse(
                name=items[0].get('name'),
                tv_id=items[0].get('tv_id'),
                values=[
                    MainChartValuesTVMinPrice(
                        min_price=i.get('price'),
                        shop=i.get('shop'),
                        link=i.get('link')) for i in items]
            ))

        pages = chart.get_count_pages(total)
        return PaginationResponseSchema[MainChartTVMinPriceResponse](
            items=res_schema,
            total=total,
            page=chart.page,
            size=chart.page_size,
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
