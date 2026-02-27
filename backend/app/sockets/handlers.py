from __future__ import annotations

import asyncio
import contextlib
import logging
import random

import socketio
from sqlalchemy import select

from app.database import async_session
from app.game.engine import GameEngine, GameError
from app.game.types import Card, GameConfig, GamePhase, Rank, ScoringVariant, Suit
from app.models.user import User
from app.services.auth_service import decode_token
from app.sockets.emitters import (
    emit_bid_placed,
    emit_card_played,
    emit_error,
    emit_game_over,
    emit_game_state,
    emit_game_state_to_all,
    emit_player_joined,
    emit_player_left,
    emit_round_scored,
    emit_trick_won,
    emit_turn_timed_out,
    emit_your_turn,
)
from app.sockets.manager import manager

logger = logging.getLogger(__name__)

NUM_AVATARS = 12


def _random_avatar_url() -> str:
    return f"/avatars/avatar-{random.randint(1, NUM_AVATARS)}.svg"


def register_handlers(sio: socketio.AsyncServer):

    @sio.event
    async def connect(sid, environ, auth):
        if not auth or "token" not in auth:
            logger.warning(f"Connection rejected: no auth token from {sid}")
            raise socketio.exceptions.ConnectionRefusedError("Authentication required")

        try:
            payload = decode_token(auth["token"])
            player_id = payload["sub"]
            display_name = payload.get("name", "Anonymous")
        except Exception as e:
            logger.warning(f"Connection rejected: invalid token from {sid}: {e}")
            raise socketio.exceptions.ConnectionRefusedError("Invalid token") from e

        # Look up avatar_url from database
        avatar_url = None
        try:
            async with async_session() as db:
                result = await db.execute(
                    select(User.avatar_url).where(User.id == player_id)
                )
                avatar_url = result.scalar_one_or_none()
        except Exception as e:
            logger.warning(f"Could not look up avatar for {player_id}: {e}")

        # Assign random avatar for users without one
        if not avatar_url:
            avatar_url = _random_avatar_url()

        manager.register_sid(sid, player_id)
        await sio.save_session(sid, {
            "player_id": player_id,
            "display_name": display_name,
            "avatar_url": avatar_url,
        })
        logger.info(f"Client connected: {sid} (player: {player_id})")

    @sio.event
    async def disconnect(sid):
        await sio.get_session(sid)
        player_id = manager.get_player_id(sid)
        if not player_id:
            return

        result = manager.get_player_engine(player_id)
        if result:
            room_code, engine = result
            if engine.state.phase != GamePhase.LOBBY:
                engine.set_player_connected(player_id, False)
                # Start auto-play timer for disconnected player
                manager.start_disconnect_timer(
                    player_id,
                    lambda pid: _auto_play(sio, room_code),
                    timeout=60.0,
                )
                for p in engine.players:
                    other_sid = manager.get_sid(p.player_id)
                    if other_sid:
                        await sio.emit(
                            "player_disconnected",
                            {"player_id": player_id},
                            to=other_sid,
                        )
            else:
                manager.leave_game(player_id)
                await emit_player_left(sio, engine, player_id)
                await _notify_lobby_update(sio)

        manager.unregister_sid(sid)
        logger.info(f"Client disconnected: {sid}")

    @sio.event
    async def join_game(sid, data):
        session = await sio.get_session(sid)
        player_id = session["player_id"]
        display_name = session["display_name"]
        avatar_url = session.get("avatar_url")
        room_code = data.get("room_code", "").strip().upper()

        if not room_code:
            await emit_error(sio, sid, "Room code required")
            return

        try:
            engine = manager.join_game(room_code, player_id, display_name, avatar_url=avatar_url)
        except GameError as e:
            await emit_error(sio, sid, str(e))
            return

        await sio.enter_room(sid, room_code)
        await emit_game_state(sio, engine, player_id)
        await emit_player_joined(sio, engine, player_id)
        await _notify_lobby_update(sio)

    @sio.event
    async def leave_game(sid, data=None):
        player_id = manager.get_player_id(sid)
        if not player_id:
            return

        result = manager.leave_game(player_id)
        if result:
            room_code, engine = result
            await sio.leave_room(sid, room_code)
            await emit_player_left(sio, engine, player_id)
            await _notify_lobby_update(sio)

    @sio.event
    async def create_game(sid, data=None):
        session = await sio.get_session(sid)
        player_id = session["player_id"]
        display_name = session["display_name"]
        avatar_url = session.get("avatar_url")

        # Parse config if provided
        config = None
        if data and "config" in data:
            cfg = data["config"]
            raw_mhs = cfg.get("max_hand_size")
            config = GameConfig(
                scoring_variant=ScoringVariant(cfg.get("scoring_variant", "standard")),
                hook_rule=cfg.get("hook_rule", True),
                turn_timer_seconds=cfg.get("turn_timer_seconds", 30),
                max_players=min(max(cfg.get("max_players", 7), 3), 7),
                max_hand_size=max(1, min(13, int(raw_mhs))) if raw_mhs is not None else None,
            )

        engine = manager.create_game(player_id, display_name, config, avatar_url=avatar_url)
        room_code = engine.room_code

        await sio.enter_room(sid, room_code)
        await emit_game_state(sio, engine, player_id)
        await _notify_lobby_update(sio)
        await sio.emit("game_created", {"room_code": room_code}, to=sid)

    @sio.event
    async def start_game(sid, data=None):
        logger.info(f"start_game event from sid={sid}")
        player_id = manager.get_player_id(sid)
        if not player_id:
            logger.warning("start_game: no player_id for sid")
            return

        result = manager.get_player_engine(player_id)
        if not result:
            await emit_error(sio, sid, "Not in a game")
            return

        room_code, engine = result
        try:
            engine.start_game(player_id)
            logger.info(
                f"Game {room_code} started. "
                f"Phase={engine.phase}, players={len(engine.players)}"
            )
        except GameError as e:
            await emit_error(sio, sid, str(e))
            return

        await emit_game_state_to_all(sio, engine)
        await _notify_lobby_update(sio)

        # Notify first bidder
        current = engine.get_current_player_id()
        logger.info(f"First bidder: {current}")
        if current:
            await emit_your_turn(sio, engine, current, engine.state.config.turn_timer_seconds)

        # Handle bot turns
        await _handle_bot_turns(sio, engine)

        # Start turn timer for the current human player
        _start_turn_timer(sio, engine, room_code)

    @sio.event
    async def place_bid(sid, data):
        player_id = manager.get_player_id(sid)
        if not player_id:
            return

        result = manager.get_player_engine(player_id)
        if not result:
            await emit_error(sio, sid, "Not in a game")
            return

        room_code, engine = result
        bid = data.get("bid")
        if bid is None:
            await emit_error(sio, sid, "Bid required")
            return

        try:
            engine.place_bid(player_id, int(bid))
        except GameError as e:
            await emit_error(sio, sid, str(e))
            return

        await emit_bid_placed(sio, engine, player_id, int(bid))

        if engine.phase == GamePhase.PLAYING:
            await emit_game_state_to_all(sio, engine)

        # Notify next player
        current = engine.get_current_player_id()
        if current:
            _cancel_turn_timer(room_code)
            await emit_your_turn(sio, engine, current, engine.state.config.turn_timer_seconds)
            await _handle_bot_turns(sio, engine)
            _start_turn_timer(sio, engine, room_code)

    @sio.event
    async def play_card(sid, data):
        player_id = manager.get_player_id(sid)
        if not player_id:
            return

        result = manager.get_player_engine(player_id)
        if not result:
            await emit_error(sio, sid, "Not in a game")
            return

        room_code, engine = result
        card_data = data.get("card")
        if not card_data:
            await emit_error(sio, sid, "Card required")
            return

        try:
            card = Card(suit=Suit(card_data["suit"]), rank=Rank(card_data["rank"]))
            trick_result = engine.play_card(player_id, card)
        except (GameError, KeyError, ValueError) as e:
            await emit_error(sio, sid, str(e))
            return

        await emit_card_played(sio, engine, player_id, card.to_dict())

        if trick_result.trick_complete:
            await emit_trick_won(sio, engine, trick_result.winner_id, trick_result.trick)
            await asyncio.sleep(1.5)  # Brief pause to show winning trick before clearing

            if trick_result.round_over:
                scores = engine.state.scores_history[-1]
                round_num = engine.state.round_number

                if engine.phase == GamePhase.GAME_OVER:
                    _cancel_turn_timer(room_code)
                    await emit_round_scored(sio, engine, scores, round_num)
                    await emit_game_over(sio, engine)
                    return
                else:
                    await emit_round_scored(sio, engine, scores, round_num)
                    # Auto-advance to next round after a brief pause
                    await asyncio.sleep(2)
                    engine.advance_to_next_round()
                    await emit_game_state_to_all(sio, engine)

        # Notify next player
        _cancel_turn_timer(room_code)
        current = engine.get_current_player_id()
        if current:
            await emit_your_turn(sio, engine, current, engine.state.config.turn_timer_seconds)
            await _handle_bot_turns(sio, engine)
            _start_turn_timer(sio, engine, room_code)

    @sio.event
    async def add_bot(sid, data=None):
        player_id = manager.get_player_id(sid)
        if not player_id:
            return

        result = manager.get_player_engine(player_id)
        if not result:
            await emit_error(sio, sid, "Not in a game")
            return

        room_code, engine = result
        if player_id != engine.state.host_id:
            await emit_error(sio, sid, "Only the host can add bots")
            return

        (data or {}).get("difficulty", "basic")
        bot_num = sum(1 for p in engine.players if p.is_bot) + 1
        bot_id = f"bot_{room_code}_{bot_num}"
        bot_name = f"Bot {bot_num}"

        try:
            engine.add_player(bot_id, bot_name, is_bot=True, avatar_url=_random_avatar_url())
        except GameError as e:
            await emit_error(sio, sid, str(e))
            return

        await emit_player_joined(sio, engine, bot_id)
        await emit_game_state_to_all(sio, engine)
        await _notify_lobby_update(sio)

    @sio.event
    async def remove_bot(sid, data):
        player_id = manager.get_player_id(sid)
        if not player_id:
            return

        result = manager.get_player_engine(player_id)
        if not result:
            await emit_error(sio, sid, "Not in a game")
            return

        room_code, engine = result
        if player_id != engine.state.host_id:
            await emit_error(sio, sid, "Only the host can remove bots")
            return

        bot_id = data.get("player_id")
        if not bot_id:
            await emit_error(sio, sid, "Bot ID required")
            return

        bot = engine.state.get_player(bot_id)
        if not bot or not bot.is_bot:
            await emit_error(sio, sid, "Player is not a bot")
            return

        try:
            engine.remove_player(bot_id)
        except GameError as e:
            await emit_error(sio, sid, str(e))
            return

        await emit_player_left(sio, engine, bot_id)
        await emit_game_state_to_all(sio, engine)
        await _notify_lobby_update(sio)

    @sio.event
    async def update_config(sid, data):
        player_id = manager.get_player_id(sid)
        if not player_id:
            return

        result = manager.get_player_engine(player_id)
        if not result:
            await emit_error(sio, sid, "Not in a game")
            return

        room_code, engine = result
        if player_id != engine.state.host_id:
            await emit_error(sio, sid, "Only the host can update config")
            return

        if engine.state.phase != GamePhase.LOBBY:
            await emit_error(sio, sid, "Cannot change config after game started")
            return

        cfg = data.get("config", {})
        if "scoring_variant" in cfg:
            engine.state.config.scoring_variant = ScoringVariant(cfg["scoring_variant"])
        if "hook_rule" in cfg:
            engine.state.config.hook_rule = bool(cfg["hook_rule"])
        if "turn_timer_seconds" in cfg:
            engine.state.config.turn_timer_seconds = max(
                10, min(120, int(cfg["turn_timer_seconds"]))
            )
        if "max_players" in cfg:
            engine.state.config.max_players = max(3, min(7, int(cfg["max_players"])))
        if "max_hand_size" in cfg:
            val = cfg["max_hand_size"]
            engine.state.config.max_hand_size = (
                max(1, min(13, int(val))) if val is not None else None
            )

        await emit_game_state_to_all(sio, engine)

    @sio.event
    async def send_chat(sid, data):
        player_id = manager.get_player_id(sid)
        if not player_id:
            return

        result = manager.get_player_engine(player_id)
        if not result:
            return

        room_code, engine = result
        session = await sio.get_session(sid)
        message = (data.get("message", ""))[:200].strip()
        if not message:
            return

        for p in engine.players:
            p_sid = manager.get_sid(p.player_id)
            if p_sid:
                await sio.emit("chat_message", {
                    "player_id": player_id,
                    "display_name": session["display_name"],
                    "message": message,
                }, to=p_sid)


def _start_turn_timer(sio: socketio.AsyncServer, engine: GameEngine, room_code: str):
    """Start a server-side turn timer for the current human player."""
    current_id = engine.get_current_player_id()
    if not current_id:
        return

    player = engine.state.get_player(current_id)
    if not player or player.is_bot:
        return

    timeout = engine.state.config.turn_timer_seconds

    async def _on_timeout(rc: str):
        await _auto_play(sio, rc)

    manager.start_turn_timer(room_code, _on_timeout, float(timeout))


def _cancel_turn_timer(room_code: str):
    """Cancel the turn timer for a room."""
    manager.cancel_turn_timer(room_code)


async def _handle_bot_turns(
    sio: socketio.AsyncServer, engine: GameEngine,
):
    """Process bot turns with delays."""
    from app.bot.basic import BasicBot

    while True:
        current_id = engine.get_current_player_id()
        if not current_id:
            logger.info("_handle_bot_turns: no current player, breaking")
            break

        player = engine.state.get_player(current_id)
        if not player or not player.is_bot:
            logger.info(f"_handle_bot_turns: current player {current_id} is not a bot, breaking")
            break

        logger.info(f"_handle_bot_turns: bot {current_id} turn, phase={engine.phase}")

        # Delay to feel natural
        await asyncio.sleep(1.5)

        bot = BasicBot()

        try:
            if engine.phase == GamePhase.BIDDING:
                valid_bids = engine.get_valid_bids_for_player(current_id)
                logger.info(f"Bot {current_id} valid bids: {valid_bids}")
                bid = bot.choose_bid(player, engine.state, valid_bids)
                logger.info(f"Bot {current_id} chose bid: {bid}")
                engine.place_bid(current_id, bid)
                await emit_bid_placed(sio, engine, current_id, bid)

                if engine.phase == GamePhase.PLAYING:
                    await emit_game_state_to_all(sio, engine)

            elif engine.phase == GamePhase.PLAYING:
                valid_cards = engine.get_valid_cards_for_player(current_id)
                card = bot.choose_card(player, engine.state, valid_cards)
                trick_result = engine.play_card(current_id, card)

                await emit_card_played(sio, engine, current_id, card.to_dict())

                if trick_result.trick_complete:
                    await emit_trick_won(sio, engine, trick_result.winner_id, trick_result.trick)

                    if trick_result.round_over:
                        scores = engine.state.scores_history[-1]
                        round_num = engine.state.round_number

                        if engine.phase == GamePhase.GAME_OVER:
                            await emit_round_scored(sio, engine, scores, round_num)
                            await emit_game_over(sio, engine)
                            return
                        else:
                            await emit_round_scored(sio, engine, scores, round_num)
                            await asyncio.sleep(2)
                            engine.advance_to_next_round()
                            await emit_game_state_to_all(sio, engine)
            else:
                break
        except Exception as e:
            logger.error(f"Bot turn error: {e}", exc_info=True)
            break

        # Notify next player
        next_id = engine.get_current_player_id()
        if next_id:
            next_player = engine.state.get_player(next_id)
            if next_player and not next_player.is_bot:
                room_code = engine.room_code
                await emit_your_turn(sio, engine, next_id, engine.state.config.turn_timer_seconds)
                _start_turn_timer(sio, engine, room_code)


async def _auto_play(sio: socketio.AsyncServer, room_code: str):
    """Auto-play for a timed-out player: bid 0, play first valid card. Handles full game flow."""
    engine = manager.get_engine(room_code)
    if not engine:
        return

    player_id = engine.get_current_player_id()
    if not player_id:
        return

    player = engine.state.get_player(player_id)
    if not player:
        return

    # Notify everyone that this player timed out
    await emit_turn_timed_out(sio, engine, player_id)

    try:
        if engine.phase == GamePhase.BIDDING:
            valid_bids = engine.get_valid_bids_for_player(player_id)
            bid = 0 if 0 in valid_bids else valid_bids[0]
            engine.place_bid(player_id, bid)
            await emit_bid_placed(sio, engine, player_id, bid)
            if engine.phase == GamePhase.PLAYING:
                await emit_game_state_to_all(sio, engine)

        elif engine.phase == GamePhase.PLAYING:
            valid_cards = engine.get_valid_cards_for_player(player_id)
            if not valid_cards:
                return
            card = valid_cards[0]
            trick_result = engine.play_card(player_id, card)
            await emit_card_played(sio, engine, player_id, card.to_dict())

            if trick_result.trick_complete:
                await emit_trick_won(sio, engine, trick_result.winner_id, trick_result.trick)
                await asyncio.sleep(1.5)

                if trick_result.round_over:
                    scores = engine.state.scores_history[-1]
                    round_num = engine.state.round_number

                    if engine.phase == GamePhase.GAME_OVER:
                        await emit_round_scored(sio, engine, scores, round_num)
                        await emit_game_over(sio, engine)
                        return
                    else:
                        await emit_round_scored(sio, engine, scores, round_num)
                        await asyncio.sleep(2)
                        engine.advance_to_next_round()
                        await emit_game_state_to_all(sio, engine)
        else:
            return
    except GameError as e:
        logger.error(f"Auto-play error for {player_id}: {e}")
        return

    # Notify next player and continue game flow
    next_id = engine.get_current_player_id()
    if next_id:
        await emit_your_turn(sio, engine, next_id, engine.state.config.turn_timer_seconds)
        await _handle_bot_turns(sio, engine)
        # After bots are done, start timer for the next human player
        final_id = engine.get_current_player_id()
        if final_id:
            final_player = engine.state.get_player(final_id)
            if final_player and not final_player.is_bot:
                _start_turn_timer(sio, engine, room_code)


async def _notify_lobby_update(sio: socketio.AsyncServer):
    """Notify lobby namespace clients of room list changes."""
    rooms = manager.get_lobby_rooms()
    # Emit to the /lobby namespace
    with contextlib.suppress(Exception):
        await sio.emit("rooms_updated", {"rooms": rooms}, namespace="/lobby")
