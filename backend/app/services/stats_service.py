from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.game.engine import GameEngine
from app.models.stats import UserStats


async def update_player_stats(db: AsyncSession, engine: GameEngine):
    """Update user stats for all human players after a game ends."""
    winner = engine.get_winner()

    for player in engine.players:
        if player.is_bot:
            continue

        try:
            user_id = uuid.UUID(player.player_id)
        except ValueError:
            continue

        result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
        stats = result.scalar_one_or_none()
        if not stats:
            stats = UserStats(user_id=user_id)
            db.add(stats)

        stats.games_played += 1

        is_winner = winner and winner.player_id == player.player_id
        if is_winner:
            stats.games_won += 1
            stats.current_streak += 1
            stats.best_streak = max(stats.best_streak, stats.current_streak)
        else:
            stats.current_streak = 0

        stats.best_score = max(stats.best_score, player.score)

        # Count round stats
        for round_scores in engine.state.scores_history:
            for score_entry in round_scores:
                if score_entry.player_id == player.player_id:
                    stats.total_rounds += 1
                    stats.total_bids += 1
                    if score_entry.bid == score_entry.tricks_won:
                        stats.exact_bids += 1

    await db.commit()
