from typing import List, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.pagination import Pagination
from src.common.password import get_password_hash
from src.common.utils import utc_now
from src.user.schemas import AddressCreate, UserCreate, UserUpdate
from src.exceptions import CustomRequestValidationError, ResourceNotFound
from src.models import User, Address


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

    async def get_or_none(
        self,
        session: AsyncSession,
        id: int,
    ) -> User | None:
        return await session.get(User, id)

    async def get(
        self,
        session: AsyncSession,
        id: int,
    ) -> User:
        user = await self.get_or_none(session, id)

        if user is None:
            raise ResourceNotFound()

        return user

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
        user_id: int,
        update_schema: UserUpdate,
    ) -> User:
        user = await self.get(session, user_id)

        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        session.add(user)
        await session.flush()
        return user

    async def delete(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> User:
        user = await self.get(session, user_id)

        await session.delete(user)
        await session.flush()
        return user

    async def get_by_username(
        self,
        session: AsyncSession,
        username: str,
    ) -> User | None:
        statement = select(User).where(User.username == username)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def update_last_login(
        self,
        session: AsyncSession,
        user: User,
    ) -> User:
        user.last_login_at = utc_now()

        session.add(user)
        await session.flush()
        return user

    async def get_address_list(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> Sequence[Address]:
        statement = select(Address).where(
            Address.user_id == user_id
        )
        result = await session.execute(statement)
        return result.scalars().all()

    async def create_address(
        self,
        session: AsyncSession,
        user_id: int,
        create_schema: AddressCreate,
    ) -> Address:
        # 기존 주소지 조회
        statement = select(Address).where(
            Address.user_id == user_id
        )
        result = await session.execute(statement)
        addresses = result.scalars().all()

        # 첫 번째 주소라면 기본 배송지로 설정
        if len(addresses) == 0:
            create_schema.is_default = True

        # 기본 배송지 설정 시 기존 기본 배송지 해제
        if create_schema.is_default:
            for addr in addresses:
                addr.is_default = False
                session.add(addr)

        address = Address(user_id=user_id, **create_schema.model_dump())
        session.add(address)
        await session.flush()
        return address


user_service = UserService()
