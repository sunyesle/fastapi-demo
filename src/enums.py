from enum import Enum


class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class OrderStatus(str, Enum):
    pending = "pending"        # 결제 대기
    paid = "paid"              # 결제 완료
    preparing = "preparing"    # 배송 준비
    shipping = "shipping"      # 배송 중
    delivered = "delivered"    # 배송 완료
    cancelled = "cancelled"    # 취소
