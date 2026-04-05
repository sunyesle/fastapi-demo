from datetime import datetime

from sqlalchemy import TIMESTAMP, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.common.utils import utc_now


class Model(DeclarativeBase):
    pass

class IDModel(Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

class TimestampedModel(Model):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=utc_now, index=True
    )
    modified_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), onupdate=utc_now, nullable=True, default=None
    )
    def set_modified_at(self) -> None:
        self.modified_at = utc_now()

class RecordModel(IDModel, TimestampedModel):
    __abstract__ = True
