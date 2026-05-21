from fastapi import APIRouter, Depends, status, HTTPException

from settings.database import get_session
from repository.matrix_type import MatrixTypeData
from schema.pagination import PaginationResponseSchema
from schema.matrix_type import (
    MatrixTypeFullSchema,
    MatrixTypeParamsSchema,
    MatrixTypeSmallSchema,
    MatrixTypeUpdateSchema,
)

router = APIRouter(prefix='/matrix_type', tags=['MatrixType'])


@router.get('/', response_model=PaginationResponseSchema[MatrixTypeFullSchema])
async def matrix_type_list(pagination: MatrixTypeParamsSchema = Depends(), session=Depends(get_session)):
    """Получить список типов матриц с пагинацией, сортировкой и фильтрацией

    параметры пагинации:
    - Страница: ?page=0
    - Количество записей на странице: ?page_size=20

    Параметры сортировки:
    - Сортировка по ID: ?sort_field=поле сортировки
      Пример сортировки по id: ?sort_field=id
    - Порядок сортировка: ?sort_order=asc (увеличение) или desc (уменьшение)

    Параметры фильтров:
    - Фильтр по id: ?id=1
    - Фильтр по названию: ?name=LED
    - Точное совпадение названия: ?name=LED
    - Название не равно: ?name_ne=LED
    - Название содержит подстроку: ?name_icontains=LED
    - Название начинается с: ?name_istartswith=LED
    - Название заканчивается на: ?name_iendswith=LED
    """
    try:
        matrix_type_data = MatrixTypeData(session)
        matrix_type_list, total = await matrix_type_data.get_multi(
            limit=pagination.limit,
            skip=pagination.offset,
            filters=pagination.filters,
            sort_field=pagination.sort_field,
            sort_order=pagination.sort_order,
        )
        pages = pagination.get_count_pages(total)
        matrix_type_schemes = [MatrixTypeFullSchema.model_validate(item) for item in matrix_type_list]

        return PaginationResponseSchema[MatrixTypeFullSchema](
            items=matrix_type_schemes,
            total=total,
            page=pagination.page,
            size=pagination.page_size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/', response_model=MatrixTypeSmallSchema)
async def matrix_type_create(matrix_type: MatrixTypeSmallSchema, session=Depends(get_session)):
    try:
        matrix_type_data = MatrixTypeData(session)
        new_matrix_type = await matrix_type_data.create(matrix_type)
        return MatrixTypeSmallSchema.model_validate(new_matrix_type)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch('/patch/{id}/', response_model=MatrixTypeSmallSchema)
async def matrix_type_update(id: int, matrix_type: MatrixTypeUpdateSchema, session=Depends(get_session)):
    try:
        matrix_type_data = MatrixTypeData(session)
        model = await matrix_type_data.update(id, matrix_type)
        return MatrixTypeSmallSchema.model_validate(model)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def matrix_type_delete(id: int, session=Depends(get_session)):
    try:
        matrix_type_data = MatrixTypeData(session)
        await matrix_type_data.delete(id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
