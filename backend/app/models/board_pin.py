import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BoardPin(Base):
    __tablename__ = "board_pins"

    board_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("boards.id", ondelete="CASCADE"), primary_key=True)
    pin_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("pins.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
