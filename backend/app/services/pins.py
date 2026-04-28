from uuid import UUID

from fastapi import HTTPException, UploadFile, status

from app.models.user import User
from app.repositories.pins import PinRepository
from app.schemas.pin import PinCreate
from app.services.storage import StorageService


class PinService:
    def __init__(self, repository: PinRepository, storage_service: StorageService):
        self.repository = repository
        self.storage = storage_service

    def create_pin(self, current_user: User, data: PinCreate, image: UploadFile):
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image uploads are allowed",
            )

        stored = self.storage.upload_image(image)
        return self.repository.create(
            owner_id=current_user.id,
            title=data.title,
            description=data.description,
            image_url=stored.url,
            image_object_key=stored.object_key,
            source_url=data.source_url,
            is_public=data.is_public,
        )

    def list_public_pins(self):
        return self.repository.list_public()

    def search_public_pins(self, query: str):
        return self.repository.search_public(query)

    def get_pin(self, pin_id: UUID):
        pin = self.repository.get_by_id(pin_id)
        if pin is None or not pin.is_public:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pin not found")
        return pin
