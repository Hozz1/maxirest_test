from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PinCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    source_url: str | None = None
    is_public: bool = True


class PinRead(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    description: str | None
    image_url: str
    image_object_key: str
    source_url: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
