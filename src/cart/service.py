from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.cart.schemas import CartItemUpdate
from src.exceptions import BadRequest, CustomException, ResourceNotFound
from src.models import Cart, CartItem, Product
from src.product.service import product_service


class CartValidationError(CustomException):
    def __init__(self, errors: list[dict], message: str = "Cart validation failed", status_code = 400) -> None:
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

    async def get_or_none(
        self,
        session: AsyncSession,
        cart_id: int,
    ) -> Cart | None:
        statement = (
            select(Cart)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
            .where(Cart.id == cart_id)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get(
        self,
        session: AsyncSession,
        cart_id: int,
    ) -> Cart:
        cart = await self.get_or_none(session, cart_id)

        if cart is None:
            raise ResourceNotFound()

        return cart

    async def add_item(
        self,
        session: AsyncSession,
        cart_id: int,
        product_id: int,
        quantity: int,
    ) -> Cart:
        cart = await self.get(session, cart_id)

        # 기존 아이템 확인
        item = next((i for i in cart.items if i.product_id == product_id), None)

        # 최종 수량 결정
        target_quantity = (item.quantity + quantity) if item else quantity

        # 상품 검증
        product = item.product if item else await product_service.get(session, product_id)
        self._validate_cart_item(
            product=product,
            requested_quantity=target_quantity,
            product_id=product_id,
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
        cart_id: int,
        item_id: int,
        update_schema: CartItemUpdate,
    ) -> Cart:
        cart = await self.get(session, cart_id)

        # 아이템 존재 여부 확인
        item = next((i for i in cart.items if i.id == item_id), None)
        if not item:
            raise ResourceNotFound()

        if update_schema.quantity is not None:
            self._validate_cart_item(
                    product=item.product,
                    requested_quantity=update_schema.quantity,
                    product_id=item.product_id,
                    item_id=item.id
                )
            item.quantity = update_schema.quantity
            cart.set_modified_at()

        await session.flush()
        return cart

    async def delete_item(
        self,
        session: AsyncSession,
        cart_id: int,
        item_id: int,
    ) -> Cart:
        cart = await self.get(session, cart_id)

        # 아이템 존재 여부 확인
        item = next((i for i in cart.items if i.id == item_id), None)
        if not item:
            raise ResourceNotFound()
        
        await session.delete(item)

        cart.set_modified_at()

        await session.flush()
        return cart

    async def merge_carts(
        self,
        session: AsyncSession,
        user_cart_id: int,
        guest_cart_id: int,
    ) -> None:
        user_cart = await self.get(session, user_cart_id)
        guest_cart = await self.get(session, guest_cart_id)

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
        id: int,
    ) -> None:
        cart = await self.get(session, id)

        errors = []
        for item in cart.items:
            try:
                self._validate_cart_item(
                    product=item.product,
                    requested_quantity=item.quantity,
                    product_id=item.product_id,
                    item_id=item.id
                )
            except CartValidationError as e:
                if e.errors:
                    errors.extend(e.errors)

        if errors:
            raise CartValidationError(
                errors=errors
            )

    def _validate_cart_item(
        self,
        product: Product | None,
        requested_quantity: int,
        product_id: int,
        item_id: int | None = None,
    ) -> None:
        msg = None

        if not product:
            msg = f"This product is no longer available."
        elif not product.is_active:
            msg = f"'{product.name}' is currently unavailable."
        elif product.stock < requested_quantity:
            msg = f"'{product.name}' has insufficient stock. (Available: {product.stock})"

        if msg:
            raise CartValidationError(
                errors=[{"item_id": item_id, "product_id": product_id, "message": msg}]
            )


cart_service = CartService()
