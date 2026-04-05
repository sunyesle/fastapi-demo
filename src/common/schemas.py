from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class IDSchema(Schema):
    id: int = Field(description="ID")

class TimestampedSchema(Schema):
    created_at: datetime = Field(description="생성일시")
    modified_at: datetime | None = Field(description="수정일시")
