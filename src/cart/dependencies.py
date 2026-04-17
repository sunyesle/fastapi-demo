import uuid

from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user_optional
from src.cart.cart_session import get_cart_session_id, set_cart_session_cookie
from src.cart.service import cart_service
from src.database import get_db_session
from src.models import User, Cart


async def get_current_cart(
    request: Request,
    response: Response,
    user: User | None = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_db_session),
) -> Cart:
    # 회원
    if user:
        return await cart_service.get_or_create(session, user_id=user.id)
    
    # 비회원
    session_id = get_cart_session_id(request)
    if session_id is None:
        session_id = str(uuid.uuid4())
        set_cart_session_cookie(response, session_id)

    return await cart_service.get_or_create(session, session_id=session_id)
