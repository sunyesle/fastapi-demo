from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.schemas import UserCreate, UserSchema
from src.user.service import user_service
from src.database import get_db_session
from src.models.user import User


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserSchema, status_code=201)
async def create(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    return await user_service.create(session, user_create)
