from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.pagination import Pagination
from src.common.password import get_password_hash
from src.user.schemas import UserCreate, UserUpdate
from src.exceptions import CustomRequestValidationError
from src.models import User


class UserService:

    async def list(
        self,
        session: AsyncSession,
        active_only: bool,
        pagination: Pagination,
    ) -> tuple[Sequence[User], int]:
        statement = select(User)

        if active_only:
            statement = statement.where(User.is_active == True)

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await session.execute(count_statement)
        count = count_result.scalar_one()

        offset = (pagination.page - 1) * pagination.size
        statement = statement.offset(offset).limit(pagination.size)
        result = await session.execute(statement)
        results = result.scalars().all()

        return results, count

    async def get(
        self,
        session: AsyncSession,
        id: int,
    ) -> User | None:
        return await session.get(User, id)

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

    async def update(
        self,
        session: AsyncSession,
        user: User,
        update_schema: UserUpdate,
    ) -> User:
        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        session.add(user)
        await session.flush()
        return user

    async def delete(
        self,
        session: AsyncSession,
        user: User,
    ) -> User:
        await session.delete(user)
        await session.flush()
        return user


user_service = UserService()
