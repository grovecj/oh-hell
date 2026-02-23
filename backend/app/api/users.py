from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.stats import UserStats
from app.services.auth_service import decode_token

router = APIRouter(tags=["users"])


async def get_current_user_id(authorization: str = Header(None)) -> str | None:
    if not authorization:
        return None
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        return payload["sub"]
    except Exception:
        return None


@router.get("/me")
async def get_profile(
    user_id: str | None = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if not user_id:
        return {"error": "Not authenticated"}

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        return {"error": "User not found"}

    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == user.id))
    stats = stats_result.scalar_one_or_none()

    return {
        "id": str(user.id),
        "display_name": user.display_name,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "is_anonymous": user.is_anonymous,
        "stats": {
            "games_played": stats.games_played if stats else 0,
            "games_won": stats.games_won if stats else 0,
            "total_rounds": stats.total_rounds if stats else 0,
            "exact_bids": stats.exact_bids if stats else 0,
            "total_bids": stats.total_bids if stats else 0,
            "bid_accuracy": (
                round(stats.exact_bids / stats.total_bids * 100, 1)
                if stats and stats.total_bids > 0
                else 0
            ),
            "best_score": stats.best_score if stats else 0,
            "current_streak": stats.current_streak if stats else 0,
            "best_streak": stats.best_streak if stats else 0,
        } if stats else None,
    }


@router.get("/leaderboard")
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User, UserStats)
        .join(UserStats, User.id == UserStats.user_id)
        .where(User.is_anonymous == False)  # noqa: E712
        .where(UserStats.games_played >= 1)
        .order_by(UserStats.games_won.desc())
        .limit(50)
    )
    rows = result.all()

    return [
        {
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
            "games_played": stats.games_played,
            "games_won": stats.games_won,
            "win_rate": round(stats.games_won / stats.games_played * 100, 1) if stats.games_played > 0 else 0,
            "bid_accuracy": round(stats.exact_bids / stats.total_bids * 100, 1) if stats.total_bids > 0 else 0,
            "best_score": stats.best_score,
            "best_streak": stats.best_streak,
        }
        for user, stats in rows
    ]
