from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_storage_service
from app.db.session import get_db
from app.models.user import User
from app.repositories.pins import PinRepository
from app.schemas.pin import PinCreate, PinRead
from app.services.pins import PinService
from app.services.storage import StorageService

router = APIRouter(prefix="/pins", tags=["pins"])


@router.post("", response_model=PinRead)
def create_pin(
    title: str = Form(...),
    description: str | None = Form(default=None),
    source_url: str | None = Form(default=None),
    is_public: bool = Form(default=True),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
) -> PinRead:
    payload = PinCreate(
        title=title,
        description=description,
        source_url=source_url,
        is_public=is_public,
    )
    pin = PinService(PinRepository(db), storage).create_pin(current_user, payload, image)
    return PinRead.model_validate(pin)


@router.get("", response_model=list[PinRead])
def list_pins(
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
) -> list[PinRead]:
    pins = PinService(PinRepository(db), storage).list_public_pins()
    return [PinRead.model_validate(pin) for pin in pins]


@router.get("/{pin_id}", response_model=PinRead)
def get_pin(
    pin_id: UUID,
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
) -> PinRead:
    pin = PinService(PinRepository(db), storage).get_pin(pin_id)
    return PinRead.model_validate(pin)
