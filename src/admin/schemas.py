from datetime import datetime

from pydantic import Field

from src.common.schemas import IDSchema, Schema, TimestampedSchema
from src.enums import OrderStatus, UserRole


class AdminOrderBase(Schema):
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

class AdminOrderSchema(AdminOrderBase, TimestampedSchema, IDSchema):
    items: list[AdminOrderItemBase] = Field(default_factory=list)

class AdminOrderItemBase(Schema):
    order_id: int
    product_id: int
    product_name: str
    product_price: int
    quantity: int
    subtotal: int

class AdminOrderItemSchema(AdminOrderItemBase, TimestampedSchema, IDSchema):
    pass

class AdminOrderStatusUpdate(Schema):
    status: OrderStatus

class AdminUserBase(Schema):
    username: str
    name: str
    phone: str | None = None
    role: UserRole
    is_active: bool
    last_login_at: datetime | None = None

class AdminUserSchema(AdminUserBase, TimestampedSchema, IDSchema):
    pass

class AdminUserStatusUpdate(Schema):
    is_active: bool
