"""
Auth service — handles registration, login, OAuth, and token management.
"""
import secrets
from typing import Optional
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import cache_set, cache_get, cache_delete
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_refresh_token
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse

logger = structlog.get_logger(__name__)

REFRESH_TOKEN_PREFIX = "refresh_token:"


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> UserResponse:
        # Check email uniqueness
        existing = await self.db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise ValueError("Email already registered")

        # Check username uniqueness
        existing_uname = await self.db.execute(select(User).where(User.username == data.username))
        if existing_uname.scalar_one_or_none():
            raise ValueError("Username already taken")

        user = User(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            auth_provider="email",
            is_verified=False,
            email_verification_token=secrets.token_urlsafe(32),
        )
        self.db.add(user)
        await self.db.flush()  # Get the ID without committing
        await self.db.refresh(user)

        logger.info("User registered", user_id=str(user.id), email=user.email)

        # Trigger welcome email in background
        try:
            from app.services.email_service import EmailService
            import asyncio
            asyncio.create_task(EmailService().send_welcome_email(user.email, user.full_name))
        except Exception:
            pass

        return UserResponse.model_validate(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        result = await self.db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not user.hashed_password:
            raise ValueError("Invalid email or password")
        if not verify_password(data.password, user.hashed_password):
            raise ValueError("Invalid email or password")
        if not user.is_active:
            raise ValueError("Account is disabled")

        return await self._create_token_pair(user)

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        user_id = verify_refresh_token(refresh_token)
        if not user_id:
            raise ValueError("Invalid or expired refresh token")

        # Check token is not revoked
        stored = await cache_get(f"{REFRESH_TOKEN_PREFIX}{user_id}")
        if stored != refresh_token:
            raise ValueError("Refresh token has been revoked")

        try:
            uid = UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            raise ValueError("Invalid user identifier in token")

        result = await self.db.execute(select(User).where(User.id == uid))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        return await self._create_token_pair(user)

    async def logout(self, user_id: str) -> None:
        await cache_delete(f"{REFRESH_TOKEN_PREFIX}{user_id}")
        logger.info("User logged out", user_id=user_id)

    async def get_or_create_google_user(
        self, google_id: str, email: str, full_name: Optional[str], avatar_url: Optional[str]
    ) -> "TokenResponse":
        # Try to find by google_id first
        result = await self.db.execute(select(User).where(User.google_id == google_id))
        user = result.scalar_one_or_none()

        if not user:
            # Try to find by email (link accounts)
            result = await self.db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

        if user:
            # Update OAuth info
            user.google_id = google_id
            user.avatar_url = avatar_url or user.avatar_url
            user.is_verified = True
        else:
            # Create new user
            username = email.split("@")[0].lower().replace(".", "_")[:30]
            # Ensure username uniqueness
            base_username = username
            counter = 1
            while True:
                existing = await self.db.execute(select(User).where(User.username == username))
                if not existing.scalar_one_or_none():
                    break
                username = f"{base_username}{counter}"
                counter += 1

            user = User(
                email=email,
                username=username,
                full_name=full_name,
                google_id=google_id,
                avatar_url=avatar_url,
                auth_provider="google",
                is_verified=True,
                is_active=True,
            )
            self.db.add(user)
            await self.db.flush()
            await self.db.refresh(user)

            # Send welcome email for new Google signups
            try:
                from app.services.email_service import EmailService
                import asyncio
                asyncio.create_task(EmailService().send_welcome_email(user.email, user.full_name))
            except Exception:
                pass

        return await self._create_token_pair(user)

    async def get_current_user(self, user_id: str) -> Optional[User]:
        try:
            uid = UUID(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            return None
        result = await self.db.execute(select(User).where(User.id == uid))
        return result.scalar_one_or_none()

    async def _create_token_pair(self, user: User) -> TokenResponse:
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Store refresh token in Redis
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
        await cache_set(f"{REFRESH_TOKEN_PREFIX}{user.id}", refresh_token, ttl_seconds=ttl)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
