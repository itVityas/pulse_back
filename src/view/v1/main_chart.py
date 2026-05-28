from fastapi import APIRouter, status, Depends

from share.my_exception import MyHttpException
from settings.database import get_session
from schema.main_chart import MainChartRequestSchema


router = APIRouter(prefix='/chart', tags=['Chart'],)


@router.get('/main_chart/', status_code=status.HTTP_200_OK)
async def get_main_chart(chart: MainChartRequestSchema, session=Depends(get_session)):
    try:
        result = {}

        for item in chart.root:
            if item.field == "date_range":
                result["date_start"] = item.data.start
                result["date_end"] = item.data.end
            elif item.field == "diagonal":
                result["diag_min"] = item.data.min
                result["diag_max"] = item.data.max
            else:
                result[item.field] = item.data

        return {"status": "success", "processed_filters": result}
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(status_code=400, detail=str(e), title='')
