from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.repositories.refresh_tokens import RefreshTokenRepository
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair

settings = get_settings()


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    def register(self, data: RegisterRequest) -> TokenPair:
        if self.user_repo.get_by_email(data.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        user = self.user_repo.create(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
        )
        return self._issue_tokens(user.id)

    def login(self, data: LoginRequest) -> TokenPair:
        user = self.user_repo.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        return self._issue_tokens(user.id)

    def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_refresh_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
            jti = payload["jti"]
            user_id = payload["sub"]
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

        persisted_token = self.token_repo.get_by_id(jti)
        if (
            persisted_token is None
            or persisted_token.revoked_at is not None
            or persisted_token.expires_at < datetime.now(tz=UTC)
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")

        if persisted_token.token_hash != hash_token(refresh_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token mismatch")

        self.token_repo.revoke(persisted_token)
        return self._issue_tokens(UUID(user_id))

    def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_refresh_token(refresh_token)
            token_id = payload["jti"]
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

        persisted_token = self.token_repo.get_by_id(token_id)
        if persisted_token is not None and persisted_token.revoked_at is None:
            self.token_repo.revoke(persisted_token)

    def _issue_tokens(self, user_id: UUID) -> TokenPair:
        token_id = uuid4()

        access_token = create_access_token(subject=str(user_id))
        refresh_token = create_refresh_token(subject=str(user_id), token_id=str(token_id))
        expires_at = datetime.now(tz=UTC) + timedelta(days=settings.refresh_token_expire_days)

        self.token_repo.create(user_id=user_id, token_hash=hash_token(refresh_token), expires_at=expires_at)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)
