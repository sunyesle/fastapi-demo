from pydantic import Field

from src.cart.schemas import CartItemSchema
from src.common.schemas import IDSchema, Schema, TimestampedSchema
from src.enums import OrderStatus
from src.user.schemas import AddressSchema


class CheckoutSchema(Schema):
    items: list[CartItemSchema] = Field(default_factory=list)
    total_price: int
    shipping_fee: int
    addresses: list[AddressSchema] = Field(default_factory=list)

class OrderBase(Schema):
    order_number: str
    user_id: int
    status: OrderStatus
    total_price: int
    shipping_fee: int
    final_price: int

    recipient: str
    phone: str
    zipcode: str
    address1: str
    address2: str | None = None
    memo: str | None = None

class OrderSchema(OrderBase, TimestampedSchema, IDSchema):
    items: list[OrderItemSchema] = Field(default_factory=list)

class OrderItemBase(Schema):
    order_id: int
    product_id: int
    product_name: str
    product_price: int
    quantity: int
    subtotal: int

class OrderItemSchema(OrderItemBase, TimestampedSchema, IDSchema):
    pass

class OrderCreate(Schema):
    recipient: str
    phone: str
    zipcode: str
    address1: str
    address2: str | None = None
    memo: str | None = None
    save_address: bool = False
