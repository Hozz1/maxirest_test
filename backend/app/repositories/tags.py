from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.tag import Tag


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Tag]:
        stmt = select(Tag).order_by(Tag.name.asc())
        return list(self.db.scalars(stmt).all())

    def get_by_name_or_slug(self, name: str, slug: str) -> Tag | None:
        stmt = select(Tag).where((func.lower(Tag.name) == name.lower()) | (Tag.slug == slug))
        return self.db.scalar(stmt)

    def create(self, name: str, slug: str) -> Tag:
        tag = Tag(name=name, slug=slug)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag
