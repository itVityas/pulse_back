from fastapi import APIRouter, status, Depends

from share.my_exception import MyHttpException
from settings.database import get_session
from schema.main_chart import MainChartRequestSchema, MainChartTVMinPriceResponse, MainChartValuesTVMinPrice
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
            chart: MainChartRequestSchema,
            session=Depends(get_session),
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

        results = await DayPriceData(session=session).get_models_min_price(
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
        res_schema = list()
        for key, items in results.items():
            res_schema.append(MainChartTVMinPriceResponse(
                name=key,
                values=[
                    MainChartValuesTVMinPrice(
                        min_price=i.get('price'),
                        shop=i.get('shop'),
                        link=i.get('link')) for i in items]
            ))
        return PaginationResponseSchema[MainChartTVMinPriceResponse](
            items=res_schema,
            total=len(res_schema),
            page=1,
            size=len(res_schema),
            pages=1
        )
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )
