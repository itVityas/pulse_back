from fastapi import APIRouter, status, Depends

from share.my_exception import MyHttpException
from settings.database import get_session
from schema.main_chart import MainChartRequestSchema
from repository.tv import TVData


router = APIRouter(prefix='/chart', tags=['Chart'],)


@router.get('/main_chart/', status_code=status.HTTP_200_OK)
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

        results = await TVData(session=session).get_for_main_chart(
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
        raise MyHttpException(status_code=400, detail=str(e), title='')
