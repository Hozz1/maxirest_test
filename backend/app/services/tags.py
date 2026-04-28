import re

from fastapi import HTTPException, status

from app.repositories.tags import TagRepository
from app.schemas.tag import TagCreate


class TagService:
    def __init__(self, tag_repo: TagRepository):
        self.tag_repo = tag_repo

    def list_tags(self):
        return self.tag_repo.list_all()

    def create_tag(self, data: TagCreate):
        slug = self._slugify(data.name)
        if self.tag_repo.get_by_name_or_slug(data.name, slug):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists")
        return self.tag_repo.create(name=data.name.strip(), slug=slug)

    @staticmethod
    def _slugify(value: str) -> str:
        normalized = value.strip().lower()
        normalized = re.sub(r"[^a-z0-9\s-]", "", normalized)
        normalized = re.sub(r"[\s_-]+", "-", normalized)
        return normalized.strip("-")
