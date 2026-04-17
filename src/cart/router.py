import uuid

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user_optional
from src.cart.cart_session import get_cart_session_id, set_cart_session_cookie
from src.cart.schemas import CartItemAdd, CartSchema
from src.cart.service import cart_service
from src.database import get_db_session
from src.models import Cart, User


router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/items", response_model=CartSchema, status_code=201)
async def add_item(
    data: CartItemAdd,
    request: Request,
    response: Response,
    user: User | None = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_db_session),
) -> Cart:
    if user:
        # 회원
        cart = await cart_service.get_or_create(session, user_id=user.id)
    else:
        # 비회원
        session_id = get_cart_session_id(request)
        if session_id is None:
            session_id = str(uuid.uuid4())
            set_cart_session_cookie(response, session_id)

        cart = await cart_service.get_or_create(session, session_id=session_id)

    await cart_service.add_item(session, cart, data.product_id, data.quantity)
    return cart
