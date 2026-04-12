from pydantic import Field

from src.category.schemas import CategorySchema
from src.common.schemas import IDSchema, Schema, TimestampedSchema


class ProductBase(Schema):
    name: str = Field(max_length=200)
    slug: str = Field(max_length=200)
    description: str | None = None
    price: int = Field(ge=0)
    original_price: int | None = None
    stock: int = Field(default=0, ge=0)
    is_active: bool = True
    is_featured: bool = False

class ProductSchema(ProductBase, TimestampedSchema, IDSchema):
    category: CategorySchema | None = None
    images: list[ProductImageSchema] = Field(default_factory=list)

class ProductCreate(ProductBase):
    category_id: int

class ProductUpdate(Schema):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    price: int | None = Field(default=None, ge=0)
    original_price: int | None = None
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    is_featured: bool | None = None
    category_id: int | None = None


class ProductImageBase(Schema):
    url: str
    alt: str | None = None
    sort_order: int = 0

class ProductImageSchema(ProductImageBase, TimestampedSchema, IDSchema):
    pass
