from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Suit(StrEnum):
    HEARTS = "hearts"
    DIAMONDS = "diamonds"
    CLUBS = "clubs"
    SPADES = "spades"


class Rank(StrEnum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

    @property
    def value_order(self) -> int:
        return list(Rank).index(self)


class GamePhase(StrEnum):
    LOBBY = "lobby"
    DEALING = "dealing"
    BIDDING = "bidding"
    PLAYING = "playing"
    SCORING = "scoring"
    GAME_OVER = "game_over"
    FINISHED = "finished"


class ScoringVariant(StrEnum):
    STANDARD = "standard"
    PROGRESSIVE = "progressive"
    BASIC = "basic"


@dataclass
class Card:
    suit: Suit
    rank: Rank

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self) -> int:
        return hash((self.suit, self.rank))

    def __repr__(self) -> str:
        return f"{self.rank.value}{self.suit.value[0].upper()}"

    def to_dict(self) -> dict:
        return {"suit": self.suit.value, "rank": self.rank.value}

    @classmethod
    def from_dict(cls, data: dict) -> Card:
        return cls(suit=Suit(data["suit"]), rank=Rank(data["rank"]))


@dataclass
class TrickCard:
    player_id: str
    card: Card


@dataclass
class PlayerState:
    player_id: str
    display_name: str
    seat_index: int
    is_bot: bool = False
    is_connected: bool = True
    avatar_url: str | None = None
    hand: list[Card] = field(default_factory=list)
    bid: int | None = None
    tricks_won: int = 0
    score: int = 0


@dataclass
class RoundState:
    round_number: int
    hand_size: int
    trump_card: Card | None
    trump_suit: Suit | None
    dealer_seat: int
    current_player_seat: int = 0
    bids: dict[str, int] = field(default_factory=dict)
    tricks: list[list[TrickCard]] = field(default_factory=list)
    current_trick: list[TrickCard] = field(default_factory=list)
    lead_suit: Suit | None = None


@dataclass
class GameConfig:
    scoring_variant: ScoringVariant = ScoringVariant.STANDARD
    hook_rule: bool = True
    turn_timer_seconds: int = 30
    max_players: int = 7
    max_hand_size: int | None = None

    def to_dict(self) -> dict:
        return {
            "scoring_variant": self.scoring_variant.value,
            "hook_rule": self.hook_rule,
            "turn_timer_seconds": self.turn_timer_seconds,
            "max_players": self.max_players,
            "max_hand_size": self.max_hand_size,
        }


@dataclass
class RoundScoreEntry:
    player_id: str
    bid: int
    tricks_won: int
    round_points: int
    cumulative_score: int


@dataclass
class GameState:
    room_code: str
    phase: GamePhase = GamePhase.LOBBY
    players: list[PlayerState] = field(default_factory=list)
    host_id: str = ""
    config: GameConfig = field(default_factory=GameConfig)
    round_state: RoundState | None = None
    round_number: int = 0
    dealer_seat: int = 0
    scores_history: list[list[RoundScoreEntry]] = field(default_factory=list)

    @property
    def player_count(self) -> int:
        return len(self.players)

    def get_player(self, player_id: str) -> PlayerState | None:
        for p in self.players:
            if p.player_id == player_id:
                return p
        return None

    def get_player_by_seat(self, seat: int) -> PlayerState | None:
        for p in self.players:
            if p.seat_index == seat:
                return p
        return None

    def effective_max_hand_size(self) -> int:
        if self.player_count == 0:
            return 0
        max_h = 52 // self.player_count
        if self.config.max_hand_size is not None:
            max_h = min(max_h, self.config.max_hand_size)
        return max_h

    def round_sequence(self) -> list[int]:
        max_h = self.effective_max_hand_size()
        up = list(range(1, max_h + 1))
        down = list(range(max_h - 1, 0, -1))
        return up + down

    def total_rounds(self) -> int:
        return len(self.round_sequence())
