from datetime import datetime

from src.common.schemas import IDSchema, Schema, TimestampedSchema
from src.enums import UserRole


class UserBase(Schema):
    username: str
    name: str
    phone: str | None = None
    role: UserRole
    is_active: bool
    last_login_at: datetime | None = None

class UserSchema(UserBase, TimestampedSchema, IDSchema):
    pass

class UserCreate(Schema):
    username: str
    password: str
    name: str
    phone: str | None = None

class UserUpdate(Schema):
    name: str | None = None
    phone: str | None = None
