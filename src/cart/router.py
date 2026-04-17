from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.cart.dependencies import get_current_cart
from src.cart.schemas import CartItemAdd, CartSchema
from src.cart.service import cart_service
from src.database import get_db_session
from src.models import Cart


router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/me", response_model=CartSchema)
async def me(
    cart: Cart = Depends(get_current_cart),
) -> Cart:
    return cart

@router.post("/items", response_model=CartSchema, status_code=201)
async def add_item(
    data: CartItemAdd,
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_session),
) -> Cart:
    await cart_service.add_item(session, cart, data.product_id, data.quantity)
    return cart
