from src.common.schemas import IDSchema, Schema, TimestampedSchema


class ProductBase(Schema):
    name: str
    price: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase, IDSchema, TimestampedSchema):
    pass

class ProductUpdate(Schema):
    name: str | None = None
    price: int | None = None
