from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.cart.schemas import CartItemUpdate
from src.exceptions import BadRequest, CustomException
from src.models import Cart, CartItem
from src.product.service import product_service


class CartValidationError(CustomException):    
    def __init__(self, errors: list[dict], message: str = "Bad request", status_code = 400) -> None:
        super().__init__(message, status_code, errors=errors)


class CartService:

    async def get_or_create(
        self,
        session: AsyncSession,
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> Cart:
        # 장바구니 조회
        statement = select(Cart).options(
            selectinload(Cart.items).selectinload(CartItem.product)
        )

        if user_id:
            statement = statement.where(Cart.user_id == user_id)
        elif session_id:
            statement = statement.where(Cart.session_id == session_id)
        else:
            raise BadRequest()

        result = await session.execute(statement)
        cart = result.scalar()

        # 장바구니가 없는 경우 생성
        if cart is None:
            cart = Cart(user_id=user_id, session_id=session_id, items=[])
            session.add(cart)
            await session.flush()

        return cart

    async def add_item(
        self,
        session: AsyncSession,
        cart: Cart,
        product_id: int,
        quantity: int,
    ) -> Cart:
        # 기존 아이템 확인
        item = next((i for i in cart.items if i.product_id == product_id), None)

        # 최종 수량 결정
        target_quantity = (item.quantity + quantity) if item else quantity

        # 상품 검증
        product = item.product if item else await product_service.get(session, product_id)
        product_service.validate_product_availability(
            product=product,
            requested_quantity=target_quantity,
        )

        # 상태 반영
        if item:
            item.quantity = target_quantity
        else:
            item = CartItem(
                cart=cart,
                product=product,
                quantity=target_quantity,
            )
            session.add(item)

        cart.set_modified_at()
        session.add(cart)

        await session.flush()
        return cart

    async def update_item(
        self,
        session: AsyncSession,
        cart: Cart,
        item: CartItem,
        update_schema: CartItemUpdate,
    ) -> Cart:
        if update_schema.quantity is not None:
            product_service.validate_product_availability(
                product=item.product,
                requested_quantity=update_schema.quantity
            )
            item.quantity = update_schema.quantity

            cart.set_modified_at()

        await session.flush()
        return cart

    async def delete_item(
        self,
        session: AsyncSession,
        cart: Cart,
        item: CartItem,
    ) -> Cart:
        await session.delete(item)

        cart.set_modified_at()

        await session.flush()
        return cart

    async def merge_carts(
        self,
        session: AsyncSession,
        user_cart: Cart,
        guest_cart: Cart,
    ) -> None:
        for guest_item in guest_cart.items:
            user_item = None

            # 회원 장바구니에 동일한 상품이 담겨 있는지 확인
            for item in user_cart.items:
                if item.product_id == guest_item.product_id:
                    user_item = item
                    break

            if user_item:
                # 동일 상품이 있다면: 수량 합산
                user_item.quantity += guest_item.quantity
                session.add(user_item)
            else:
                # 동일 상품이 없다면: 아이템 생성
                new_item = CartItem(
                    cart_id=user_cart.id,
                    product_id=guest_item.product_id,
                    quantity=guest_item.quantity
                )
                session.add(new_item)

        # 비회원 장바구니 삭제
        await session.delete(guest_cart)

    async def validate_cart(
        self,
        session: AsyncSession,
        cart: Cart
    ) -> None:
        errors = []

        for item in cart.items:
            product = await product_service.get(session, item.product_id)

            if not product:
                errors.append({
                    "item_id": item.id,
                    "message": f"'{item.product.name}' is no longer available."
                })
                continue

            if not product.is_active:
                errors.append({
                    "item_id": item.id,
                    "message": f"'{product.name}' is currently unavailable."
                })
                
                continue

            if product.stock < item.quantity:
                errors.append({
                    "item_id": item.id,
                    "message": f"'{product.name}' has insufficient stock. (Available: {product.stock})"
                })

        if errors:
            raise CartValidationError(message="Invalid items found in your cart.", errors=errors)


cart_service = CartService()
