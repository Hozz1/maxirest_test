import uuid

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PinTag(Base):
    __tablename__ = "pin_tags"

    pin_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("pins.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
