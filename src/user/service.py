from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.password import get_password_hash
from src.user.schemas import UserCreate
from src.exceptions import CustomRequestValidationError
from src.models.user import User


class UserService:

    async def create(
        self,
        session: AsyncSession,
        create_schema: UserCreate,
    ) -> User:
        if await self.username_exists(session, create_schema.username):
            raise CustomRequestValidationError(
                [
                    {
                        "loc": ("body", "username"),
                        "msg": "User with this username already exists.",
                        "type": "value_error",
                        "input": create_schema.username,
                    }
                ]
            )
        
        hashed_password = get_password_hash(create_schema.password)

        user = User(**create_schema.model_dump(exclude={"password"}), hashed_password=hashed_password)
        session.add(user)
        await session.flush()
        return user


    async def username_exists(
        self,
        session: AsyncSession,
        username: str,
    ) -> bool:
        statement = select(User).where(User.username == username)
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None


user_service = UserService()
