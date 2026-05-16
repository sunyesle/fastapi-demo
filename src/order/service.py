import random
import string
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.cart.schemas import CartItemSchema
from src.cart.service import cart_service
from src.common.pagination import Pagination
from src.common.utils import utc_now
from src.enums import OrderStatus
from src.models import Address
from src.models.order import Order, OrderItem
from src.order.schemas import CheckoutSchema, OrderCreate
from src.user.schemas import AddressSchema
from src.user.service import user_service
from src.product.service import product_service
from src.cart.service import cart_service


class OrderService():
    FREE_SHIPPING_THRESHOLD = 50_000  # 5만 원 이상 무료
    SHIPPING_FEE = 3_000              # 기본 배송비 3천 원

    def calculate_shipping_fee(
            self,
            total_price: int
    ) -> int:
        if total_price >= self.FREE_SHIPPING_THRESHOLD:
            return 0
        return self.SHIPPING_FEE

    @staticmethod
    def generate_order_number() -> str:
        """
        주문번호 생성
        형식: YYYYMMDD-XXXXXX (예: 20260420-A3B2C1)
        """
        date_part = utc_now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{date_part}-{random_part}"

    async def get_checkout(
        self,
        session: AsyncSession,
        cart_id: int,
    ) -> CheckoutSchema:
        # 장바구니 검증
        await cart_service.validate_cart(session, cart_id)

        # 장바구니 조회
        cart = await cart_service.get(session, cart_id)

        item_schemas = [CartItemSchema.model_validate(item) for item in cart.items]
        total_price = sum(item.product.price * item.quantity for item in cart.items)
        shipping_fee = self.calculate_shipping_fee(total_price)

        # 주소지 조회
        addresses = []
        if cart.user_id is not None:
            addresses : Sequence[Address] = await user_service.get_address_list(session, cart.user_id)

        address_schemas = [AddressSchema.model_validate(address) for address in addresses]

        return CheckoutSchema(
            items = item_schemas,
            total_price = total_price,
            shipping_fee = shipping_fee,
            addresses = address_schemas,
        )

    async def create_order(
        self,
        session: AsyncSession,
        user_id: int,
        cart_id: int,
        create_schema: OrderCreate,
    ) -> Order:
        # 장바구니 검증
        await cart_service.validate_cart(session, cart_id)

        # 장바구니 조회
        cart = await cart_service.get(session, cart_id)

        total_price = sum(item.product.price * item.quantity for item in cart.items)
        shipping_fee = self.calculate_shipping_fee(total_price)

        order_number = self.generate_order_number()
        order = await self._insert_order(
            session=session,
            user_id=user_id,
            order_number=order_number,
            total_price=total_price,
            shipping_fee=shipping_fee,
            cart_items=cart.items,
            create_schema=create_schema,
        )

        # 재고 차감
        for item in cart.items:
            await product_service.decrease_stock(
                session=session,
                product_id=item.product_id,
                quantity=item.quantity
            )

        # 장바구니 비우기
        await cart_service.clear_cart(
            session=session,
            cart_id=cart_id,
        )

        await session.flush()
        return order

    async def _insert_order(
        self,
        session: AsyncSession,
        user_id: int,
        order_number: str,
        total_price: int,
        shipping_fee: int,
        cart_items: list,
        create_schema: OrderCreate,
    ) -> Order:
        # 주문 생성
        order = Order(
            order_number=order_number,
            user_id=user_id,
            total_price=total_price,
            shipping_fee=shipping_fee,
            final_price=total_price + shipping_fee,
            recipient=create_schema.recipient,
            phone=create_schema.phone,
            zipcode=create_schema.zipcode,
            address1=create_schema.address1,
            address2=create_schema.address2,
            memo=create_schema.memo
        )
        session.add(order)

        # 주문 상품 생성
        for item in cart_items:
            subtotal = item.product.price * item.quantity

            order_item = OrderItem(
                product_id=item.product_id,
                product_name=item.product.name,
                product_price=item.product.price,
                quantity=item.quantity,
                subtotal=subtotal
            )

            order.items.append(order_item)

        await session.flush()
        return order

    async def list(
        self,
        session: AsyncSession,
        pagination: Pagination,
        user_id: int,
        status: OrderStatus | None = None,
    ) -> tuple[Sequence[Order], int]:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
        ).where(Order.user_id == user_id)

        if status is not None:
            statement = statement.where(Order.status == status)
        
        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await session.execute(count_statement)
        count = count_result.scalar_one()

        offset = (pagination.page - 1) * pagination.size
        statement = statement.offset(offset).limit(pagination.size)
        result = await session.execute(statement)
        results = result.scalars().all()

        return results, count


order_service = OrderService()
