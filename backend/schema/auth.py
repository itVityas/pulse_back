from datetime import datetime

from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class TokenPayloadSchema(BaseModel):
    sub: str
    exp: datetime
    type: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str
