from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from model.user import User
from service.security import (
    decode_access_token,)
from settings.database import get_session

security = HTTPBearer()


async def get_current_user(
                    request: Request,
                    session: AsyncSession = Depends(get_session),
                    credential: HTTPAuthorizationCredentials = Depends(security),):
    token = credential.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user_id = payload.get("id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Wrong payload")

    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.is_active is False:
        raise HTTPException(status_code=401, detail="User is deactivated")

    request.state.token = token
    return user
