from io import BytesIO

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import selectinload

from settings.database import get_session
from schema.file_upload import FileUploadSchema, FileUploadModelResponseSchema, FileUploadRequestSchema
from service.upload_file import file_upload_handle
from repository.day_price import DayPriceData
from share.my_exception import MyHttpException
from repository.file import FileUploadData
from schema.pagination import PaginationResponseSchema
from model.file import FileUpload


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


@router.get('/get_file_list/', response_model=PaginationResponseSchema[FileUploadModelResponseSchema])
async def file_upload_get(
            filter_schema: FileUploadRequestSchema = Depends(),
            session=Depends(get_session)
        ):
    """Получить список загруженных файлов
    параметры пагинации:
    - Страница: ?page=0
    - Количество записей на странице: ?page_size=20

    Параметры сортировки:
    - Сортировка по ID: ?sort_field=поле сортировки
      Пример сортировки по id: ?sort_field=id
    - Порядок сортировка: ?sort_order=asc (увеличение) или desc (уменьшение)

    Параметры фильтров:
    - Фильтр по id__eq: ?id=1
    - Фильтр по date: ?date__eq=2020-01-01
    """
    try:
        eager_options = [
            selectinload(FileUpload.shop),
            selectinload(FileUpload.currency),
        ]
        tv_list, total = await FileUploadData(session).get_multi(
            skip=filter_schema.offset,
            limit=filter_schema.limit,
            sort_field=filter_schema.sort_field,
            sort_order=filter_schema.sort_order,
            filters=filter_schema.filters,
            eager_loads=eager_options,
        )
        file_upload_schemas = [FileUploadModelResponseSchema.model_validate(item) for item in tv_list]
        pages = filter_schema.get_count_pages(total)
        return PaginationResponseSchema[FileUploadModelResponseSchema](
            items=file_upload_schemas,
            total=total,
            page=filter_schema.page,
            size=filter_schema.page_size,
            pages=pages,
        )
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )


@router.delete('/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def file_upload_delete(id: int, session=Depends(get_session)):
    try:
        await FileUploadData(session).delete(id)
        return {"detail": "Файл удален"}
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )
