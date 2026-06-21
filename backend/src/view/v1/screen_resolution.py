from fastapi import APIRouter, Depends, status

from settings.database import get_session
from repository.screen_resolution import ScreenResolutionData
from schema.pagination import PaginationResponseSchema
from schema.screen_resolution import (
    ScreenResolutionFullSchema,
    ScreenResolutionParamFilterSchema,
    ScreenResolutionSmallSchema,
    ScreenResolutionUpdateSchema,
)
from share.my_exception import MyHttpException


router = APIRouter(prefix='/screen_resolutions', tags=['ScreenResolutions'])


@router.get('/', response_model=PaginationResponseSchema[ScreenResolutionFullSchema])
async def screen_resolutions_list(
            pagination: ScreenResolutionParamFilterSchema = Depends(),
            session=Depends(get_session)):
    """Получить список разрешений экрана с пагинацией, сортировкой и фильтрацией

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
    - Ширина экрана: ?width=1920
    - Высота экрана: ?height=1080
    """
    try:
        screen_resolution_data = ScreenResolutionData(session)
        screen_resolutions, total = await screen_resolution_data.get_multi(
            limit=pagination.limit,
            skip=pagination.offset,
            filters=pagination.filters,
            sort_field=pagination.sort_field,
            sort_order=pagination.sort_order,
        )
        screen_resolution_schemes = [
            ScreenResolutionFullSchema.model_validate(screen_resolution) for screen_resolution in screen_resolutions]
        pages = pagination.get_count_pages(total)
        return PaginationResponseSchema[ScreenResolutionFullSchema](
            items=screen_resolution_schemes,
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


@router.post('/', response_model=ScreenResolutionSmallSchema)
async def screen_resolution_create(
            screen_resolution: ScreenResolutionSmallSchema,
            session=Depends(get_session)
        ):
    try:
        screen_resolution_data = ScreenResolutionData(session)
        new_screen_resolution = await screen_resolution_data.create(screen_resolution)
        return ScreenResolutionSmallSchema.model_validate(new_screen_resolution)
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )


@router.patch('/patch/{id}/', response_model=ScreenResolutionSmallSchema)
async def screen_resolution_update(
        id: int,
        screen_resolution: ScreenResolutionUpdateSchema,
        session=Depends(get_session)):
    try:
        screen_resolution_data = ScreenResolutionData(session)
        model = await screen_resolution_data.update(id, screen_resolution)
        return ScreenResolutionSmallSchema.model_validate(model)
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )


@router.delete('/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def screen_resolution_delete(id: int, session=Depends(get_session)):
    try:
        screen_resolution_data = ScreenResolutionData(session)
        await screen_resolution_data.delete(id)
    except MyHttpException:
        raise
    except Exception as e:
        raise MyHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
                title='Ошибка backend'
            )
