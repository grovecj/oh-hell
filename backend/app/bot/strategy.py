from __future__ import annotations

from abc import ABC, abstractmethod

from app.game.types import Card, GameState, PlayerState


class BotStrategy(ABC):
    @abstractmethod
    def choose_bid(self, player: PlayerState, state: GameState, valid_bids: list[int]) -> int:
        ...

    @abstractmethod
    def choose_card(self, player: PlayerState, state: GameState, valid_cards: list[Card]) -> Card:
        ...
