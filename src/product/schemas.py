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

class ProductSchema(ProductBase, IDSchema, TimestampedSchema):
    category: CategorySchema | None = None

class ProductCreate(ProductBase):
    category_id: int
