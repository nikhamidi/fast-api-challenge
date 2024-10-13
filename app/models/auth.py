"""Auth response models."""

from datetime import timedelta

from pydantic import BaseModel

from jwt_services import ACCESS_EXPIRES, REFRESH_EXPIRES


class AccessToken(BaseModel):
    access_token: str
    access_token_expires: timedelta = ACCESS_EXPIRES


class RefreshToken(AccessToken):
    refresh_token: str
    refresh_token_expires: timedelta = REFRESH_EXPIRES
