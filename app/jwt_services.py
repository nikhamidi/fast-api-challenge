from datetime import timedelta

from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer, JwtRefreshBearer
from fastapi import HTTPException, Security, status

from conf.config import Config
from models.user import User

ACCESS_EXPIRES = timedelta(minutes=60)
REFRESH_EXPIRES = timedelta(days=30)

access_security = JwtAccessBearer(
    Config.app_settings.get("secret"),
    access_expires_delta=ACCESS_EXPIRES,
    refresh_expires_delta=REFRESH_EXPIRES,
)

refresh_security = JwtRefreshBearer(
    Config.app_settings.get("secret"),
    access_expires_delta=ACCESS_EXPIRES,
    refresh_expires_delta=REFRESH_EXPIRES,
)


async def user_from_credentials(auth: JwtAuthorizationCredentials) -> User | None:
    return await User.by_username(auth.subject["username"])


async def user_from_token(token: str) -> User | None:
    payload = access_security._decode(token)
    return await User.by_username(payload["subject"]["username"])

async def current_user(
    auth: JwtAuthorizationCredentials = Security(access_security)
) -> User:
    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No authorization credentials found")
    try:
        user = await user_from_credentials(auth)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Authorized user could not be found")
    return user
