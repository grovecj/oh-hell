from __future__ import annotations

import json
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.game.engine import GameEngine
from app.models.game import Game, GameParticipant, GameRound, RoundScore


async def persist_game_results(db: AsyncSession, engine: GameEngine):
    """Persist completed game results to the database."""
    winner = engine.get_winner()

    game = Game(
        id=uuid.uuid4(),
        room_code=engine.room_code,
        scoring_variant=engine.state.config.scoring_variant.value,
        round_count=engine.state.round_number,
        player_count=engine.state.player_count,
        winner_id=uuid.UUID(winner.player_id) if winner and not winner.is_bot else None,
        status="finished",
        config_json=json.dumps(engine.state.config.to_dict()),
    )
    db.add(game)

    # Create participants
    participants: dict[str, GameParticipant] = {}
    sorted_players = sorted(engine.players, key=lambda p: p.score, reverse=True)

    for rank, player in enumerate(sorted_players, 1):
        participant = GameParticipant(
            id=uuid.uuid4(),
            game_id=game.id,
            user_id=uuid.UUID(player.player_id) if not player.is_bot else None,
            display_name=player.display_name,
            is_bot=player.is_bot,
            seat_index=player.seat_index,
            final_score=player.score,
            final_rank=rank,
        )
        db.add(participant)
        participants[player.player_id] = participant

    # Create rounds and scores
    for round_idx, round_scores in enumerate(engine.state.scores_history):
        rs = engine.state.round_state
        game_round = GameRound(
            id=uuid.uuid4(),
            game_id=game.id,
            round_number=round_idx + 1,
            hand_size=engine.state.round_sequence()[round_idx] if round_idx < len(engine.state.round_sequence()) else 0,
            trump_suit=None,
            dealer_seat=round_idx % engine.state.player_count,
        )
        db.add(game_round)

        for score_entry in round_scores:
            participant = participants.get(score_entry.player_id)
            if participant:
                round_score = RoundScore(
                    id=uuid.uuid4(),
                    round_id=game_round.id,
                    participant_id=participant.id,
                    bid=score_entry.bid,
                    tricks_won=score_entry.tricks_won,
                    round_points=score_entry.round_points,
                    cumulative_score=score_entry.cumulative_score,
                )
                db.add(round_score)

    await db.commit()
    return game
