from fastapi import APIRouter, status, Depends

from settings.database import get_session
from repository.os import OSData
from schema.pagination import PaginationResponseSchema
from schema.os import (
    OSFullSchema,
    OSParamFilterSchema,
    OSSmallSchema,
    OSUpdateSchema,
)
from share.my_exception import MyHttpException


router = APIRouter(prefix="/os", tags=["OS"],)


@router.get('/', response_model=PaginationResponseSchema[OSFullSchema])
async def os_list(
            pagination: OSParamFilterSchema = Depends(),
            session=Depends(get_session)
        ):
    """Получить список операционных систем с пагинацией, сортировкой и фильтрацией

    параметры пагинации:
    - Страница: ?page=0
    - Количество записей на странице: ?page_size=20

    Параметры сортировки:
    - Сортировка по ID: ?sort_field=поле сортировки
      Пример сортировки по id: ?sort_field=id
    - Порядок сортировка: ?sort_order=asc (увеличение) или desc (уменьшение)

    Параметры фильтров:
    - Фильтр по id: ?id=1
    - Фильтр по названию: ?name=Linux
    - Точное совпадение названия: ?name=Linux
    - Название не равно: ?name_ne=Linux
    - Название содержит подстроку: ?name_icontains=Linux
    - Название начинается с: ?name_istartswith=Linux
    - Название заканчивается на: ?name_iendswith=Linux
    """
    try:
        os_data = OSData(session)
        os_list, total = await os_data.get_multi(
            limit=pagination.limit,
            skip=pagination.offset,
            filters=pagination.filters,
            sort_field=pagination.sort_field,
            sort_order=pagination.sort_order,
        )
        pages = pagination.get_count_pages(total)
        os_schemes = [OSFullSchema.model_validate(item) for item in os_list]

        return PaginationResponseSchema[OSFullSchema](
            items=os_schemes,
            total=total,
            page=pagination.page,
            size=pagination.page_size,
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


@router.post('/', response_model=OSSmallSchema)
async def os_create(os: OSSmallSchema, session=Depends(get_session)):
    try:
        os_data = OSData(session)
        new_os = await os_data.create(os)
        return OSSmallSchema.model_validate(new_os)
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )


@router.patch('/patch/{id}/', response_model=OSSmallSchema)
async def os_update(id: int, os: OSUpdateSchema, session=Depends(get_session)):
    try:
        os_data = OSData(session)
        model = await os_data.update(id, os)
        return OSSmallSchema.model_validate(model)
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )


@router.delete('/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def os_delete(id: int, session=Depends(get_session)):
    try:
        os_data = OSData(session)
        await os_data.delete(id)
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )
