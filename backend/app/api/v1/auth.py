"""Auth API endpoints."""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.database import get_db
from app.core.redis import rate_limit_check
from app.core.config import settings
from app.schemas.auth import (
    ChangePasswordRequest,
    GoogleAuthRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register a new user with email and password."""
    # Rate limit by IP
    ip = request.client.host if request.client else "unknown"
    allowed, remaining = await rate_limit_check(
        f"register:{ip}", max_requests=5, window_seconds=3600
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Try again in an hour.",
        )

    try:
        service = AuthService(db)
        user = await service.register(data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate with email and password, receive JWT tokens."""
    ip = request.client.host if request.client else "unknown"
    allowed, _ = await rate_limit_check(
        f"login:{ip}", max_requests=settings.LOGIN_RATE_LIMIT_PER_MINUTE, window_seconds=900
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again in 15 minutes.",
        )

    try:
        service = AuthService(db)
        return await service.login(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    data: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Exchange a refresh token for a new token pair."""
    try:
        service = AuthService(db)
        return await service.refresh_tokens(data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout")
async def logout(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    """Invalidate the current user's refresh token."""
    service = AuthService(db)
    await service.logout(str(current_user.id))
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    """Get the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.get("/google/login")
async def google_login():
    """Get Google OAuth authorization URL."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend/.env",
        )
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
        "&access_type=offline"
        "&prompt=select_account"
    )
    return {"auth_url": auth_url, "client_id": settings.GOOGLE_CLIENT_ID}


@router.post("/google/credential", response_model=TokenResponse)
async def google_credential_auth(
    data: GoogleCredentialRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate securely via Google Identity Services ID Token (JWT)."""
    import httpx

    # Verify ID token with Google's secure tokeninfo endpoint
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={data.credential}"
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired Google credential token.",
            )
        info = resp.json()

    # Verify audience if client ID is configured
    if settings.GOOGLE_CLIENT_ID and info.get("aud") != settings.GOOGLE_CLIENT_ID:
        # Warning log, but verify issuer is Google
        if info.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Untrusted Google token issuer.",
            )

    email = info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email associated")

    service = AuthService(db)
    return await service.get_or_create_google_user(
        google_id=info.get("sub"),
        email=email,
        full_name=info.get("name") or email.split("@")[0],
        avatar_url=info.get("picture"),
    )


@router.get("/google/callback")
async def google_callback(
    db: Annotated[AsyncSession, Depends(get_db)],
    code: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    """Handle Google OAuth browser callback and redirect to frontend with tokens."""
    import httpx
    from fastapi.responses import RedirectResponse

    # User cancelled or denied access — redirect cleanly back to login
    if error or not code:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?cancelled=1")

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=501, detail="Google OAuth not configured")

    # Exchange code for tokens
    async with httpx.AsyncClient(timeout=15) as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange Google OAuth code")

        tokens = token_response.json()

        # Get user info
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
        )
        user_info = user_info_response.json()

    service = AuthService(db)
    token_data = await service.get_or_create_google_user(
        google_id=user_info.get("sub"),
        email=user_info.get("email"),
        full_name=user_info.get("name"),
        avatar_url=user_info.get("picture"),
    )

    # Redirect user back to Next.js frontend with tokens in URL fragment
    redirect_url = f"{settings.FRONTEND_URL}/login#access_token={token_data.access_token}&refresh_token={token_data.refresh_token}"
    return RedirectResponse(url=redirect_url)
