from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    role: UserRole
    avatar_url: str | None
    bio: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
