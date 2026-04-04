from src.common.schemas import IDSchema, Schema


class ItemBase(Schema):
    name: str
    price: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase, IDSchema):
    pass

class ItemUpdate(Schema):
    name: str | None = None
    price: int | None = None
