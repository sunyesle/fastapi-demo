from pydantic import Field

from src.common.schemas import IDSchema, Schema, TimestampedSchema


class CartBase(Schema):
    user_id: int | None = None
    session_id: str | None = None

class CartSchema(CartBase, TimestampedSchema, IDSchema):
    items: list[CartItemSchema] = Field(default_factory=list)


class CartItemBase(Schema):
    product_id: int
    quantity: int = 1

class CartItemSchema(CartItemBase, TimestampedSchema, IDSchema):
    cart_id: int
    product: ProductSimpleSchema

class CartItemAdd(Schema):
    product_id: int
    quantity: int = Field(default=1, ge=1)

class CartItemUpdate(Schema):
    quantity: int | None = Field(ge=1)


class ProductSimpleSchema(Schema):
    name: str
    slug: str
    price: int
    original_price: int | None = None
    stock: int
