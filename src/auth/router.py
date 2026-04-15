from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.service import auth_service
from src.common import jwt
from src.config import settings
from src.database import get_db_session


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_db_session)
):
    user = await auth_service.authenticate(session, form_data.username, form_data.password)

    access_token = jwt.encode(data={"sub": user.username}, secret=settings.SECRET_KEY)
    return {"access_token": access_token, "token_type": "bearer"}
