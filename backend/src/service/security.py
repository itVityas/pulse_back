from datetime import timedelta, datetime

from jose import JWTError, jwt
from passlib.context import CryptContext

from settings.config import jwt_config
from model.user import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hash_password: str) -> bool:
    return pwd_context.verify(plain_password, hash_password)


def create_access_token(user: User) -> str:
    exp_date = datetime.now(tz=None) + timedelta(minutes=jwt_config.expire_access_token)
    to_encode = {
        'id': user.id,
        'is_admin': user.is_admin,
        'exp': exp_date,
        'iat': datetime.now(tz=None),
        'type': 'access',
    }
    encoded_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.algorithm)
    return encoded_jwt


def create_refresh_token(user: User) -> str:
    exp_date = datetime.now(tz=None) + timedelta(minutes=jwt_config.expire_refresh_token)
    to_encode = {
        'id': user.id,
        'is_admin': user.is_admin,
        'exp': exp_date,
        'iat': datetime.now(tz=None),
        'type': 'refresh',
    }
    encoded_jwt = jwt.encode(to_encode, jwt_config.refresh_key, algorithm=jwt_config.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.algorithm])
        return payload
    except JWTError:
        raise ValueError("Invalid access token")


def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, jwt_config.refresh_key, algorithms=[jwt_config.algorithm])
        return payload
    except JWTError:
        raise ValueError("Invalid refresh token")
