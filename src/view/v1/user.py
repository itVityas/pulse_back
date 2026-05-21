from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select, delete

from schema.user import (
    UserGetSchema,
    UserCreateSchema,
    UserChangePasswordSchema,
    UserChangeActionSchema,
    UserPaginationParamsSchema,
    UserLoginSchema,
)
from schema.pagination import PaginationResponseSchema
from schema.auth import TokenSchema, RefreshTokenSchema
from repository.user import UserData
from model.user import User
from model.refresh_token import RefreshToken
from settings.database import get_session
from repository.auth import get_current_user
from service.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,)


router = APIRouter(prefix="/users", tags=["Users"])


@router.get('/', response_model=PaginationResponseSchema[UserGetSchema])
async def get_users(
        pagination: UserPaginationParamsSchema = Depends(),
        session=Depends(get_session)):
    """
    Получить список пользователей с пагинацией, сортировкой и фильтрацией

    Параметры пагинации:
    - Страница: ?page=0
    - Количество записей на странице: ?page_size=20

    Параметры сортировки:
    - Сортировка по ID: ?sort_field=id
    - Сортировка по username: ?sort_field=username
    - Сортировка по дате создания: ?sort_field=created_at
    - Сортировка по дате обновления: ?sort_field=updated_at
    - Обратная сортировка: ?sort_order=asc или desc

    Примеры фильтров:
    - Фильтр по username: ?username=john
    - Фильтр по части username: ?username__icontains=jo
    - Фильтр по ID: ?id=1
    - Фильтр по диапазону ID: ?id__gt=10&filters[id__lt]=50
    - Фильтр по дате: ?created_at__gte=2024-01-01T00:00:00
    - Несколько фильтров: ?is_active=true&filters[is_admin]=false
    """
    try:
        user_model = UserData(session)
        users, total = await user_model.get_multi(
            skip=pagination.offset,
            limit=pagination.limit,
            sort_field=pagination.sort_field,
            sort_order=pagination.sort_order,
            filters=pagination.filters)
        users_schema = [UserGetSchema.model_validate(user) for user in users]
        pages = total // pagination.page_size + (1 if total % pagination.page_size else 0)
        return PaginationResponseSchema[UserGetSchema](
            items=users_schema,
            total=total,
            page=pagination.page,
            size=pagination.page_size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/', response_model=UserGetSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSchema, session=Depends(get_session)):
    try:
        user_model = UserData(session)
        new_user = await user_model.create(user)
        return UserGetSchema.model_validate(new_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put('/change_password/', response_model=UserGetSchema)
async def change_password_user(user: UserChangePasswordSchema, session=Depends(get_session)):
    try:
        user_data = UserData(session)
        model = await user_data.change_password(
            id=user.id, password=user.new_password, old_password=user.old_password)
        return UserGetSchema.model_validate(model)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put('/change_active/', response_model=UserGetSchema)
async def change_active_user(
            user: UserChangeActionSchema,
            current_user: User = Depends(get_current_user),
            session=Depends(get_session)
        ):
    try:
        user_data = UserData(session)
        model = await user_data.change_state(id=user.id, is_active=user.is_active)
        return UserGetSchema.model_validate(model)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/login/', response_model=TokenSchema)
async def login_user(login_schema: UserLoginSchema, request: Request, session=Depends(get_session)):
    try:
        user = await UserData(session).authenticate(login_schema.username, login_schema.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        payload = decode_refresh_token(refresh_token)
        expires_at = datetime.fromtimestamp(payload["exp"]) if payload else None

        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
            ip_address=client_ip,
            user_agent=user_agent)
        session.add(db_refresh_token)
        await session.commit()

        return TokenSchema(access_token=access_token, refresh_token=refresh_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/refresh/', response_model=TokenSchema)
async def refresh_token(token: RefreshTokenSchema, request: Request, session=Depends(get_session)):
    try:
        result = await session.execute(select(RefreshToken).where(RefreshToken.token == token.refresh_token))
        db_refresh_token = result.scalar_one_or_none()
        if not db_refresh_token or db_refresh_token.revoked or db_refresh_token.expires_at < datetime.now(tz=None):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")
        payload = decode_refresh_token(db_refresh_token.token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token payload")
        user = await UserData(session).get_one(int(payload.get("id")))
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

        query = delete(RefreshToken).where(RefreshToken.user_id == user.id)
        await session.execute(query)
        query = delete(RefreshToken).where(
            RefreshToken.revoked == True,
            RefreshToken.expires_at < datetime.now(tz=None))
        await session.execute(query)

        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        payload = decode_refresh_token(refresh_token)

        client_ip = request.client.host if request.client else None
        expires_at = datetime.fromtimestamp(payload["exp"]) if payload else None
        user_agent = request.headers.get("user-agent")
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
            ip_address=client_ip,
            user_agent=user_agent)
        session.add(db_refresh_token)
        await session.commit()

        return TokenSchema(access_token=access_token, refresh_token=refresh_token)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
