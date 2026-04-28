import os
from collections.abc import Generator
from dataclasses import dataclass
from uuid import uuid4

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["AUTO_CREATE_TABLES"] = "false"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test-refresh-secret"

from app.core.dependencies import get_storage_service  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.services.storage import StorageService  # noqa: E402


@dataclass
class DummyStoredObject:
    object_key: str
    url: str


class DummyStorageService(StorageService):
    def upload_image(self, file: UploadFile):
        ext = ".jpg"
        if file.filename and "." in file.filename:
            ext = "." + file.filename.rsplit(".", 1)[-1]
        key = f"pins/{uuid4()}{ext}"
        return DummyStoredObject(object_key=key, url=f"http://test-storage/{key}")


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_storage_service() -> StorageService:
        return DummyStorageService()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage_service] = override_storage_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
