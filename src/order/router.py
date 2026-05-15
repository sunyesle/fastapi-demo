from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from src.cart.dependencies import get_current_cart
from src.database import get_db_read_session
from src.models import Cart
from src.order.schemas import CheckoutSchema
from src.order.service import order_service


router = APIRouter(prefix="", tags=["orders"])

@router.get("/orders/checkout", response_model=CheckoutSchema)
async def checkout(
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_read_session),
) -> CheckoutSchema:
    return await order_service.get_checkout(session, cart.id)
