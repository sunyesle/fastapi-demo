from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.cart.dependencies import get_current_cart
from src.cart.schemas import CartItemAdd, CartItemUpdate, CartSchema
from src.cart.service import cart_service
from src.database import get_db_session
from src.exceptions import ResourceNotFound
from src.models import Cart


router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/me", response_model=CartSchema)
async def me(
    cart: Cart = Depends(get_current_cart),
) -> Cart:
    return cart

@router.post("/me/items", response_model=CartSchema, status_code=201)
async def add_item(
    data: CartItemAdd,
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_session),
) -> Cart:
    await cart_service.add_item(session, cart, data.product_id, data.quantity)
    return cart

@router.put("/me/items/{item_id}", response_model=CartSchema)
async def update_item(
    item_id: int,
    data: CartItemUpdate,
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_session),
) -> Cart:
    # 수량 업데이트
    return await cart_service.update_item(
        session,
        cart=cart,
        item_id=item_id,
        update_schema=data
    )

@router.delete("/me/items/{item_id}", status_code=204)
async def delete_item(
    item_id: int,
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    # 아이템 존재 여부 확인
    item = next((i for i in cart.items if i.id == item_id), None)
    if not item:
        raise ResourceNotFound()

    await cart_service.delete_item(
        session,
        cart=cart,
        item=item,
    )

@router.post("/me/validate")
async def validate(
    cart: Cart = Depends(get_current_cart),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    await cart_service.validate_cart(session, cart)
