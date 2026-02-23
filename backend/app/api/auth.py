from __future__ import annotations

import uuid

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.stats import UserStats
from app.services.auth_service import create_token, decode_token

router = APIRouter(tags=["auth"])

oauth = OAuth()
if settings.google_client_id:
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


@router.post("/anonymous")
async def create_anonymous(db: AsyncSession = Depends(get_db)):
    user_id = uuid.uuid4()
    display_name = f"Player-{str(user_id)[:6].upper()}"

    user = User(
        id=user_id,
        display_name=display_name,
        is_anonymous=True,
    )
    db.add(user)
    db.add(UserStats(user_id=user_id))
    await db.commit()

    token = create_token(str(user_id), "anon", display_name)
    return {"token": token, "user_id": str(user_id), "display_name": display_name}


@router.get("/google")
async def google_login(request: Request, state: str | None = None):
    if not settings.google_client_id:
        return {"error": "Google OAuth not configured"}

    redirect_uri = settings.google_redirect_uri
    return await oauth.google.authorize_redirect(
        request, redirect_uri, state=state or ""
    )


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.google_client_id:
        return {"error": "Google OAuth not configured"}

    token_data = await oauth.google.authorize_access_token(request)
    user_info = token_data.get("userinfo", {})
    google_id = user_info.get("sub")
    email = user_info.get("email")
    name = user_info.get("name", "Unknown")
    picture = user_info.get("picture")

    if not google_id:
        return RedirectResponse(f"{settings.frontend_url}/login?error=no_google_id")

    # Check if user exists
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    # Check if linking anonymous account
    anon_token = request.query_params.get("state", "")
    anon_user = None
    if anon_token:
        try:
            payload = decode_token(anon_token)
            if payload.get("type") == "anon":
                anon_result = await db.execute(
                    select(User).where(User.id == uuid.UUID(payload["sub"]))
                )
                anon_user = anon_result.scalar_one_or_none()
        except Exception:
            pass

    if user:
        # Existing Google user — merge anonymous stats if applicable
        if anon_user and anon_user.is_anonymous:
            await _merge_anonymous_stats(db, anon_user, user)
    elif anon_user and anon_user.is_anonymous:
        # Upgrade anonymous user to Google account
        anon_user.google_id = google_id
        anon_user.email = email
        anon_user.display_name = name
        anon_user.avatar_url = picture
        anon_user.is_anonymous = False
        user = anon_user
    else:
        # Create new Google user
        user = User(
            id=uuid.uuid4(),
            google_id=google_id,
            email=email,
            display_name=name,
            avatar_url=picture,
            is_anonymous=False,
        )
        db.add(user)
        db.add(UserStats(user_id=user.id))

    await db.commit()

    jwt_token = create_token(str(user.id), "user", user.display_name)
    return RedirectResponse(f"{settings.frontend_url}/login?token={jwt_token}")


async def _merge_anonymous_stats(db: AsyncSession, anon_user: User, target_user: User):
    """Merge anonymous user's stats into target Google user."""
    anon_stats_result = await db.execute(
        select(UserStats).where(UserStats.user_id == anon_user.id)
    )
    anon_stats = anon_stats_result.scalar_one_or_none()

    target_stats_result = await db.execute(
        select(UserStats).where(UserStats.user_id == target_user.id)
    )
    target_stats = target_stats_result.scalar_one_or_none()

    if anon_stats and target_stats:
        target_stats.games_played += anon_stats.games_played
        target_stats.games_won += anon_stats.games_won
        target_stats.total_rounds += anon_stats.total_rounds
        target_stats.exact_bids += anon_stats.exact_bids
        target_stats.total_bids += anon_stats.total_bids
        target_stats.best_score = max(target_stats.best_score, anon_stats.best_score)
