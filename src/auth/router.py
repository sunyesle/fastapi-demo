from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.schemas import Token
from src.auth.service import auth_service
from src.cart.cart_session import get_cart_session_id
from src.cart.service import cart_service
from src.common import jwt
from src.config import settings
from src.database import get_db_session


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_db_session)
) -> Token:
    user = await auth_service.authenticate(session, form_data.username, form_data.password)

    guest_session_id = get_cart_session_id(request)
    if guest_session_id:
        try:
            guest_cart = await cart_service.get_or_create(session, session_id=guest_session_id)
            if guest_cart.items:
                user_cart = await cart_service.get_or_create(session, user_id=user.id)

                await cart_service.merge_carts(session, user_cart, guest_cart)

        except Exception:
            pass # 병합에 실패해도 로그인은 진행

    access_token = jwt.encode(data={"sub": user.username}, secret=settings.SECRET_KEY)
    return Token(access_token=access_token, token_type="bearer")
