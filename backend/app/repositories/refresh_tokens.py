from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: UUID, token_hash: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_by_id(self, token_id: str | UUID) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.id == token_id)
        return self.db.scalar(stmt)

    def revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(tz=UTC)
        self.db.add(token)
        self.db.commit()
