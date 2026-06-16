from typing import List

from fastapi import APIRouter, status, Depends

from settings.database import get_session
from share.my_exception import MyHttpException
from repository.day_price import DayPriceData
from schema.compare import CompareRequestSchema, CompareResponseSchema


router = APIRouter(prefix='/compare', tags=['Compare'])


@router.get('/compare_price/', status_code=status.HTTP_200_OK, response_model=List[CompareResponseSchema])
async def get_compare_price(
            parametrs: CompareRequestSchema = Depends(),
            session=Depends(get_session)
        ):
    try:
        results = await DayPriceData(session=session).get_compare_price_table(
            date_start=parametrs.date_start,
            date_end=parametrs.date_end,
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
