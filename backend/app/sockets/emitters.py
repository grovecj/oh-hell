from __future__ import annotations

import socketio

from app.game.engine import GameEngine
from app.game.types import GamePhase, RoundScoreEntry, TrickCard
from app.sockets.manager import manager


async def emit_game_state(sio: socketio.AsyncServer, engine: GameEngine, player_id: str):
    """Send full game state to a specific player."""
    sid = manager.get_sid(player_id)
    if sid:
        view = engine.get_player_view(player_id)
        import logging
        logging.getLogger("app.sockets.emitters").info(
            f"Sending game_state to {player_id}: phase={view['phase']}, hand={view['hand']}, "
            f"current_player_id={view['current_player_id']}"
        )
        await sio.emit("game_state", view, to=sid)


async def emit_game_state_to_all(sio: socketio.AsyncServer, engine: GameEngine):
    """Send filtered game state to all players in the game."""
    for p in engine.players:
        await emit_game_state(sio, engine, p.player_id)


async def emit_to_room(sio: socketio.AsyncServer, engine: GameEngine, event: str, data: dict):
    """Emit an event to all connected players in a game."""
    for p in engine.players:
        sid = manager.get_sid(p.player_id)
        if sid:
            await sio.emit(event, data, to=sid)


async def emit_player_joined(sio: socketio.AsyncServer, engine: GameEngine, player_id: str):
    player = engine.state.get_player(player_id)
    if player:
        await emit_to_room(sio, engine, "player_joined", {
            "player": {
                "id": player.player_id,
                "display_name": player.display_name,
                "seat_index": player.seat_index,
                "is_bot": player.is_bot,
                "is_connected": player.is_connected,
                "avatar_url": player.avatar_url,
                "card_count": 0,
                "bid": None,
                "tricks_won": 0,
                "score": 0,
            }
        })


async def emit_player_left(sio: socketio.AsyncServer, engine: GameEngine, player_id: str):
    await emit_to_room(sio, engine, "player_left", {"player_id": player_id})


async def emit_bid_placed(sio: socketio.AsyncServer, engine: GameEngine, player_id: str, bid: int):
    await emit_to_room(sio, engine, "bid_placed", {
        "player_id": player_id,
        "bid": bid,
        "current_player_id": engine.get_current_player_id(),
        "phase": engine.phase.value,
    })


async def emit_card_played(sio: socketio.AsyncServer, engine: GameEngine, player_id: str, card_dict: dict):
    await emit_to_room(sio, engine, "card_played", {
        "player_id": player_id,
        "card": card_dict,
        "current_player_id": engine.get_current_player_id(),
    })


async def emit_trick_won(sio: socketio.AsyncServer, engine: GameEngine, winner_id: str, trick: list[TrickCard]):
    await emit_to_room(sio, engine, "trick_won", {
        "winner_id": winner_id,
        "trick": [{"player_id": tc.player_id, "card": tc.card.to_dict()} for tc in trick],
    })


async def emit_round_scored(sio: socketio.AsyncServer, engine: GameEngine, scores: list[RoundScoreEntry], round_number: int):
    await emit_to_room(sio, engine, "round_scored", {
        "scores": [
            {
                "player_id": s.player_id,
                "bid": s.bid,
                "tricks_won": s.tricks_won,
                "round_points": s.round_points,
                "cumulative_score": s.cumulative_score,
            }
            for s in scores
        ],
        "round_number": round_number,
    })


async def emit_game_over(sio: socketio.AsyncServer, engine: GameEngine):
    winner = engine.get_winner()
    last_scores = engine.state.scores_history[-1] if engine.state.scores_history else []
    await emit_to_room(sio, engine, "game_over", {
        "final_scores": [
            {
                "player_id": s.player_id,
                "bid": s.bid,
                "tricks_won": s.tricks_won,
                "round_points": s.round_points,
                "cumulative_score": s.cumulative_score,
            }
            for s in last_scores
        ],
        "winner_id": winner.player_id if winner else None,
    })


async def emit_your_turn(sio: socketio.AsyncServer, engine: GameEngine, player_id: str, timer: int = 30):
    """Notify a player it's their turn with valid actions."""
    sid = manager.get_sid(player_id)
    if not sid:
        return

    if engine.phase == GamePhase.PLAYING:
        valid_cards = engine.get_valid_cards_for_player(player_id)
        await sio.emit("your_turn", {
            "valid_cards": [c.to_dict() for c in valid_cards],
            "time_remaining": timer,
        }, to=sid)
    elif engine.phase == GamePhase.BIDDING:
        valid_bids = engine.get_valid_bids_for_player(player_id)
        await sio.emit("your_turn", {
            "valid_bids": valid_bids,
            "time_remaining": timer,
        }, to=sid)


async def emit_error(sio: socketio.AsyncServer, sid: str, message: str):
    await sio.emit("error", {"message": message}, to=sid)
