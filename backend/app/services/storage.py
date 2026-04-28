from dataclasses import dataclass
import io
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from minio import Minio

from app.core.config import get_settings

settings = get_settings()


@dataclass
class StoredObject:
    object_key: str
    url: str


class StorageService:
    def upload_image(self, file: UploadFile) -> StoredObject:
        raise NotImplementedError


class MinioStorageService(StorageService):
    def __init__(self) -> None:
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket = settings.minio_bucket

    def upload_image(self, file: UploadFile) -> StoredObject:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

        extension = Path(file.filename or "image.jpg").suffix or ".jpg"
        object_key = f"pins/{uuid4()}{extension}"

        file.file.seek(0)
        data = file.file.read()

        self.client.put_object(
            self.bucket,
            object_key,
            data=io.BytesIO(data),
            length=len(data),
            content_type=file.content_type or "application/octet-stream",
        )

        public_url = f"{settings.minio_public_base_url}/{self.bucket}/{object_key}"
        return StoredObject(object_key=object_key, url=public_url)
