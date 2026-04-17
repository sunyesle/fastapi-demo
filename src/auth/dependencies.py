from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.auth.schemas import TokenData
from src.common import jwt
from src.config import settings
from src.database import get_db_read_session
from src.exceptions import Unauthorized
from src.models import User
from src.user.service import user_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

async def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_read_session),
) -> User | None:

    if not token:
        return None

    try:
        payload = jwt.decode(token=token, secret=settings.SECRET_KEY)
        username = payload.get("sub")

        if username is None:
            return None

        token_data = TokenData(username=username)

    except InvalidTokenError:
        return None

    user = await user_service.get_by_username(session, username=token_data.username)
    return user

async def get_current_user(
    current_user: User | None = Depends(get_current_user_optional),
) -> User:
    if current_user is None:
        raise Unauthorized()
    return current_user
