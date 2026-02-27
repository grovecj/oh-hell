from __future__ import annotations

import asyncio
import logging

from app.game.engine import GameEngine, GameError, generate_room_code
from app.game.types import GameConfig, GamePhase

logger = logging.getLogger(__name__)


class GameRoomManager:
    """Manages active game rooms and player-to-room mappings."""

    def __init__(self):
        self.games: dict[str, GameEngine] = {}  # room_code → GameEngine
        self.player_rooms: dict[str, str] = {}  # player_id → room_code
        self.sid_to_player: dict[str, str] = {}  # socket sid → player_id
        self.player_to_sid: dict[str, str] = {}  # player_id → socket sid
        self._disconnect_tasks: dict[str, asyncio.Task] = {}  # player_id → auto-play task
        self._turn_timers: dict[str, asyncio.Task] = {}  # room_code → turn timer task

    def create_game(self, host_id: str, host_name: str, config: GameConfig | None = None, avatar_url: str | None = None) -> GameEngine:
        room_code = generate_room_code()
        while room_code in self.games:
            room_code = generate_room_code()

        engine = GameEngine(room_code=room_code, config=config)
        engine.add_player(host_id, host_name, avatar_url=avatar_url)
        self.games[room_code] = engine
        self.player_rooms[host_id] = room_code
        return engine

    def join_game(self, room_code: str, player_id: str, display_name: str, avatar_url: str | None = None) -> GameEngine:
        engine = self.games.get(room_code)
        if not engine:
            raise GameError("Game not found")
        if engine.state.phase != GamePhase.LOBBY:
            # Check if reconnecting
            player = engine.state.get_player(player_id)
            if player:
                player.is_connected = True
                self.player_rooms[player_id] = room_code
                self._cancel_disconnect_timer(player_id)
                return engine
            raise GameError("Game already in progress")

        engine.add_player(player_id, display_name, avatar_url=avatar_url)
        self.player_rooms[player_id] = room_code
        return engine

    def leave_game(self, player_id: str) -> tuple[str, GameEngine] | None:
        room_code = self.player_rooms.pop(player_id, None)
        if not room_code:
            return None

        engine = self.games.get(room_code)
        if not engine:
            return None

        if engine.state.phase == GamePhase.LOBBY:
            engine.remove_player(player_id)
            if not engine.players:
                del self.games[room_code]
        else:
            engine.set_player_connected(player_id, False)

        return room_code, engine

    def get_engine(self, room_code: str) -> GameEngine | None:
        return self.games.get(room_code)

    def get_player_engine(self, player_id: str) -> tuple[str, GameEngine] | None:
        room_code = self.player_rooms.get(player_id)
        if not room_code:
            return None
        engine = self.games.get(room_code)
        if not engine:
            return None
        return room_code, engine

    def register_sid(self, sid: str, player_id: str):
        self.sid_to_player[sid] = player_id
        self.player_to_sid[player_id] = sid

    def unregister_sid(self, sid: str) -> str | None:
        player_id = self.sid_to_player.pop(sid, None)
        if player_id:
            self.player_to_sid.pop(player_id, None)
        return player_id

    def get_player_id(self, sid: str) -> str | None:
        return self.sid_to_player.get(sid)

    def get_sid(self, player_id: str) -> str | None:
        return self.player_to_sid.get(player_id)

    def get_lobby_rooms(self) -> list[dict]:
        rooms = []
        for code, engine in self.games.items():
            if engine.state.phase in (GamePhase.LOBBY, GamePhase.BIDDING, GamePhase.PLAYING, GamePhase.SCORING):
                rooms.append({
                    "room_code": code,
                    "host_name": engine.players[0].display_name if engine.players else "Unknown",
                    "player_count": len(engine.players),
                    "max_players": engine.state.config.max_players,
                    "scoring_variant": engine.state.config.scoring_variant.value,
                    "status": "waiting" if engine.state.phase == GamePhase.LOBBY else "in_progress",
                })
        return rooms

    def start_disconnect_timer(self, player_id: str, callback, timeout: float = 60.0):
        self._cancel_disconnect_timer(player_id)

        async def _timer():
            await asyncio.sleep(timeout)
            await callback(player_id)

        self._disconnect_tasks[player_id] = asyncio.create_task(_timer())

    def _cancel_disconnect_timer(self, player_id: str):
        task = self._disconnect_tasks.pop(player_id, None)
        if task:
            task.cancel()

    def start_turn_timer(self, room_code: str, callback, timeout: float):
        """Cancel any existing turn timer for the room and start a new one."""
        self.cancel_turn_timer(room_code)

        async def _timer():
            await asyncio.sleep(timeout)
            await callback(room_code)

        self._turn_timers[room_code] = asyncio.create_task(_timer())

    def cancel_turn_timer(self, room_code: str):
        """Cancel the turn timer for a room if one exists."""
        task = self._turn_timers.pop(room_code, None)
        if task:
            task.cancel()

    def cleanup_game(self, room_code: str):
        self.cancel_turn_timer(room_code)
        engine = self.games.pop(room_code, None)
        if engine:
            for p in engine.players:
                self.player_rooms.pop(p.player_id, None)
                self._cancel_disconnect_timer(p.player_id)


# Singleton instance
manager = GameRoomManager()
