from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, null
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.models import RecordModel

if TYPE_CHECKING:
    from src.models.category import Category


class Product(RecordModel):
    __tablename__ = "products"
    
    name: Mapped[str] = mapped_column(String)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    price: Mapped[int] = mapped_column(Integer)
    original_price: Mapped[int | None] = mapped_column(Integer, nullable=True) # 원래 가격 (할인 표시용)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False) # 추천 상품
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), default=None)

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(back_populates="product")

class ProductImage(RecordModel):
    __tablename__ = "product_images"

    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    url: Mapped[str] = mapped_column(String)
    alt: Mapped[str | None] = mapped_column(String, default=None)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship("Product", back_populates="images")
