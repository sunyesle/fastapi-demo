from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from src.common.models import RecordModel


class User(RecordModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    disabled: Mapped[bool] = mapped_column(Boolean, default=True)
