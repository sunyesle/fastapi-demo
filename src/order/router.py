from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.cart.dependencies import get_current_cart
from src.common.pagination import Page, PaginationQuery
from src.database import get_db_read_session, get_db_session
from src.enums import OrderStatus
from src.models import Cart
from src.models.order import Order
from src.models.user import User
from src.order.schemas import CheckoutSchema, OrderCreate, OrderSchema
from src.order.service import order_service


router = APIRouter(prefix="", tags=["orders"])

@router.get("/orders/checkout", response_model=CheckoutSchema)
async def checkout(
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_read_session),
) -> CheckoutSchema:
    return await order_service.get_checkout(session, cart.id)

@router.post("/orders", response_model=OrderSchema, status_code=201)
async def create(
    order_create: OrderCreate,
    user: User = Depends(get_current_user),
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_session),
) -> Order:
    return await order_service.create_order(session, user.id, cart.id, order_create)

@router.get("/me/orders", response_model=Page[OrderSchema])
async def list(
    pagination: PaginationQuery,
    status: OrderStatus | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_read_session),
) -> Page[OrderSchema]:
    results, count = await order_service.list(
        session,
        user_id=user.id,
        status=status,
        pagination=pagination,
    )

    return Page.from_paginated_results(
        [OrderSchema.model_validate(r) for r in results],
        count,
        pagination
    )
