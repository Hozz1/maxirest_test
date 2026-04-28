from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BoardCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    is_public: bool = True


class BoardUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_public: bool | None = None


class BoardRead(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    description: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
