from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.pin import Pin
from app.models.pin_tag import PinTag
from app.models.tag import Tag


class PinRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        owner_id: UUID,
        title: str,
        description: str | None,
        image_url: str,
        image_object_key: str,
        source_url: str | None,
        is_public: bool,
    ) -> Pin:
        pin = Pin(
            owner_id=owner_id,
            title=title,
            description=description,
            image_url=image_url,
            image_object_key=image_object_key,
            source_url=source_url,
            is_public=is_public,
        )
        self.db.add(pin)
        self.db.commit()
        self.db.refresh(pin)
        return pin

    def list_public(self, limit: int = 50) -> list[Pin]:
        stmt = select(Pin).where(Pin.is_public.is_(True)).order_by(Pin.created_at.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, pin_id: UUID) -> Pin | None:
        stmt = select(Pin).where(Pin.id == pin_id)
        return self.db.scalar(stmt)

    def search_public(self, query: str, limit: int = 50) -> list[Pin]:
        q = f"%{query}%"
        stmt = (
            select(Pin)
            .outerjoin(PinTag, PinTag.pin_id == Pin.id)
            .outerjoin(Tag, Tag.id == PinTag.tag_id)
            .where(
                Pin.is_public.is_(True),
                or_(
                    Pin.title.ilike(q),
                    Pin.description.ilike(q),
                    Tag.name.ilike(q),
                    Tag.slug.ilike(q),
                ),
            )
            .order_by(Pin.created_at.desc())
            .distinct()
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
