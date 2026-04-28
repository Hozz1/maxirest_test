from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.schemas.tag import TagCreate, TagRead
from app.services.tags import TagService
from app.repositories.tags import TagRepository

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)) -> list[TagRead]:
    tags = TagService(TagRepository(db)).list_tags()
    return [TagRead.model_validate(tag) for tag in tags]


@router.post("", response_model=TagRead)
def create_tag(
    data: TagCreate,
    _: object = Depends(require_admin),
    db: Session = Depends(get_db),
) -> TagRead:
    tag = TagService(TagRepository(db)).create_tag(data)
    return TagRead.model_validate(tag)
