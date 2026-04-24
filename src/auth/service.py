from sqlalchemy.ext.asyncio import AsyncSession

from src.common.password import verify_password
from src.exceptions import Forbidden, Unauthorized
from src.models import User
from src.user.service import user_service


class AuthService:

    async def authenticate(
        self,
        session: AsyncSession,
        username: str,
        password: str
    ) -> User:
        user = await user_service.get_by_username(session, username)

        if user is None:
            raise Unauthorized()

        if not verify_password(password, user.hashed_password):
            raise Unauthorized()

        if not user.is_active:
            raise Forbidden("Inactive user")

        await user_service.update_last_login(session, user)

        return user

auth_service = AuthService()
