from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.cart.dependencies import get_current_cart
from src.cart.schemas import CartItemAdd, CartItemUpdate, CartSchema
from src.cart.service import cart_service
from src.database import get_db_read_session, get_db_session
from src.exceptions import ResourceNotFound
from src.models import Cart


router = APIRouter(prefix="", tags=["cart"])


@router.get("/me/cart", response_model=CartSchema)
async def me(
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_read_session),
) -> Cart:
    return await cart_service.get(session, cart.id)

@router.post("/me/cart/items", response_model=CartSchema, status_code=201)
async def add_item(
    data: CartItemAdd,
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_session),
) -> Cart:
    await cart_service.add_item(session, cart.id, data.product_id, data.quantity)
    return cart

@router.put("/me/cart/items/{item_id}", response_model=CartSchema)
async def update_item(
    item_id: int,
    data: CartItemUpdate,
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_session),
) -> Cart:
    # 수량 업데이트
    return await cart_service.update_item(
        session,
        cart_id=cart.id,
        item_id=item_id,
        update_schema=data
    )

@router.delete("/me/cart/items/{item_id}", status_code=204)
async def delete_item(
    item_id: int,
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    await cart_service.delete_item(
        session,
        cart_id=cart.id,
        item_id=item_id,
    )

@router.post("/me/cart/validate")
async def validate(
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    await cart_service.validate_cart(session, cart.id)
