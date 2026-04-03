from pydantic import BaseModel, ConfigDict, Field


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class IDSchema(Schema):
    id: int = Field(description="ID")
