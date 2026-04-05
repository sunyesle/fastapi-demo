from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.common.models import RecordModel


class Item(RecordModel):
    __tablename__ = "items"
    
    name: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
