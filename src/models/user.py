from datetime import datetime

from sqlalchemy import TIMESTAMP, Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.common.models import RecordModel
from src.enums import UserRole


class User(RecordModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, default=None)
