from typing import List

from fastapi import APIRouter, status, Depends

from settings.database import get_session
from share.my_exception import MyHttpException
from repository.day_price import DayPriceData
from schema.compare import CompareResponseSchema
from schema.main_chart import MainChartRequestSchema


router = APIRouter(prefix='/compare', tags=['Compare'])


@router.post('/compare_price/', status_code=status.HTTP_200_OK, response_model=List[CompareResponseSchema])
async def get_compare_price(
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
        results = await DayPriceData(session=session).get_compare_price_table(
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
        res_schema = [CompareResponseSchema.model_validate(item) for item in results]
        return res_schema
    except MyHttpException:
        raise
    except Exception as ex:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ex),
                title='Ошибка backend'
            )
