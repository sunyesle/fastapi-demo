from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.cart.schemas import CartItemSchema
from src.cart.service import cart_service
from src.models import Address
from src.order.schemas import CheckoutSchema
from src.user.schemas import AddressSchema
from src.user.service import user_service


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


order_service = OrderService()
