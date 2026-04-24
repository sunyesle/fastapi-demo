from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.models import RecordModel
from src.models.product import Product
from src.models.user import User


class Cart(RecordModel):
    __tablename__ = "carts"

    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String, nullable=True) # 비회원용

    user: Mapped["User"] = relationship()
    items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(RecordModel):
    __tablename__ = "cart_items"

    cart_id: Mapped[int] = mapped_column(Integer, ForeignKey("carts.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(default=1)

    cart: Mapped["Cart"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()
