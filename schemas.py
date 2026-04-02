from pydantic import BaseModel, ConfigDict


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class ItemBase(Schema):
    name: str
    price: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

class ItemUpdate(Schema):
    name: str | None = None
    price: int | None = None
