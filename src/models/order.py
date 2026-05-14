from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.models import RecordModel
from src.enums import OrderStatus

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.product import Product


class Order(RecordModel):
    __tablename__ = "orders"

    order_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # 주문 정보
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.pending)
    total_price: Mapped[int] = mapped_column(Integer)  # 상품 금액
    shipping_fee: Mapped[int] = mapped_column(Integer, default=0)  # 배송비
    final_price: Mapped[int] = mapped_column(Integer)  # 최종 결제 금액

    # 배송 정보
    recipient: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    zipcode: Mapped[str] = mapped_column(String)
    address1: Mapped[str] = mapped_column(String)
    address2: Mapped[str | None] = mapped_column(String, nullable=True)
    memo: Mapped[str | None] = mapped_column(String, nullable=True)

    # 시간
    paid_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, default=None)
    shipped_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, default=None)
    delivered_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, default=None)
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, default=None)

    user: Mapped["User"] = relationship("User")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(RecordModel):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))

    # 주문 당시 정보 (상품 정보가 변경되어도 주문 내역은 유지)
    product_name: Mapped[str] = mapped_column(String)
    product_price: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    subtotal: Mapped[int] = mapped_column(Integer)

    # 관계
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")