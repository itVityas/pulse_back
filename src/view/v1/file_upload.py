from io import BytesIO

from fastapi import APIRouter, Depends, status, UploadFile, File

from settings.database import get_session
from schema.file_upload import FileUploadSchema
from service.upload_file import file_upload_handle
from repository.day_price import DayPriceData
from share.my_exception import MyHttpException


router = APIRouter(prefix='/file_upload', tags=['FileUpload'])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def file_upload(
                        parameters: FileUploadSchema = Depends(),
                        file: UploadFile = File(),
                        session=Depends(get_session)):
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=file.filename,
                title="Только файлы Excel (.xlsx, .xls) разрешены"
            )
        day_price = await DayPriceData(session).get_by_shop_date(
            parameters.shop_id,
            parameters.date)
        if len(day_price) > 0:
            raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=len(day_price),
                title="Данные за этот день уже загружены"
            )
        contents = await file.read()
        file_stream = BytesIO(contents)
        await file_upload_handle(
            file_stream,
            parameters.currency_id,
            parameters.shop_id,
            parameters.date, session,
            file_size=len(contents),
            filename=file.filename)
        return {"filename": file.filename}
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )
