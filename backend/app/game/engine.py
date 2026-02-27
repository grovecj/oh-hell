from __future__ import annotations

import random
import string

from app.game.deck import create_deck, deal, shuffle_deck
from app.game.rules import (
    determine_trick_winner,
    get_valid_bids,
    get_valid_cards,
    is_valid_bid,
    is_valid_play,
)
from app.game.scoring import calculate_score
from app.game.types import (
    Card,
    GameConfig,
    GamePhase,
    GameState,
    PlayerState,
    RoundScoreEntry,
    RoundState,
    TrickCard,
)


def generate_room_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class GameError(Exception):
    pass


class GameEngine:
    def __init__(self, room_code: str | None = None, config: GameConfig | None = None):
        self.state = GameState(
            room_code=room_code or generate_room_code(),
            config=config or GameConfig(),
        )
        self._rng = random.Random()

    @property
    def phase(self) -> GamePhase:
        return self.state.phase

    @property
    def players(self) -> list[PlayerState]:
        return self.state.players

    @property
    def room_code(self) -> str:
        return self.state.room_code

    def add_player(
        self, player_id: str, display_name: str,
        is_bot: bool = False, avatar_url: str | None = None,
    ) -> PlayerState:
        if self.state.phase != GamePhase.LOBBY:
            raise GameError("Cannot add players after game has started")
        if len(self.state.players) >= self.state.config.max_players:
            raise GameError("Game is full")
        if self.state.get_player(player_id):
            raise GameError("Player already in game")

        seat = len(self.state.players)
        player = PlayerState(
            player_id=player_id,
            display_name=display_name,
            seat_index=seat,
            is_bot=is_bot,
            avatar_url=avatar_url,
        )
        self.state.players.append(player)

        if not self.state.host_id:
            self.state.host_id = player_id

        return player

    def remove_player(self, player_id: str) -> None:
        if self.state.phase != GamePhase.LOBBY:
            raise GameError("Cannot remove players after game has started")

        player = self.state.get_player(player_id)
        if not player:
            raise GameError("Player not in game")

        self.state.players.remove(player)

        # Re-seat remaining players
        for i, p in enumerate(self.state.players):
            p.seat_index = i

        # If host left, assign new host
        if self.state.host_id == player_id and self.state.players:
            self.state.host_id = self.state.players[0].player_id

    def start_game(self, player_id: str) -> None:
        if player_id != self.state.host_id:
            raise GameError("Only the host can start the game")
        if len(self.state.players) < 3:
            raise GameError("Need at least 3 players")
        if self.state.phase != GamePhase.LOBBY:
            raise GameError("Game already started")

        self.state.dealer_seat = 0
        self.state.round_number = 0
        self._start_round()

    def _start_round(self) -> None:
        sequence = self.state.round_sequence()
        if self.state.round_number >= len(sequence):
            self.state.phase = GamePhase.GAME_OVER
            return

        hand_size = sequence[self.state.round_number]
        dealer_seat = self.state.dealer_seat % self.state.player_count

        # Reset player state for new round
        for p in self.state.players:
            p.hand = []
            p.bid = None
            p.tricks_won = 0

        # Deal cards
        deck = shuffle_deck(create_deck(), self._rng)
        hands, trump_card = deal(deck, self.state.player_count, hand_size)
        trump_suit = trump_card.suit if trump_card else None

        for i, _p in enumerate(self.state.players):
            # Deal by seat order starting left of dealer
            deal_idx = (dealer_seat + 1 + i) % self.state.player_count
            p_at_seat = self.state.get_player_by_seat(deal_idx)
            if p_at_seat:
                p_at_seat.hand = hands[i]

        # First bidder is left of dealer
        first_bidder_seat = (dealer_seat + 1) % self.state.player_count

        self.state.round_state = RoundState(
            round_number=self.state.round_number,
            hand_size=hand_size,
            trump_card=trump_card,
            trump_suit=trump_suit,
            dealer_seat=dealer_seat,
            current_player_seat=first_bidder_seat,
        )

        self.state.phase = GamePhase.BIDDING

    def place_bid(self, player_id: str, bid: int) -> None:
        if self.state.phase != GamePhase.BIDDING:
            raise GameError("Not in bidding phase")

        rs = self.state.round_state
        if rs is None:
            raise GameError("No round in progress")

        current_player = self.state.get_player_by_seat(rs.current_player_seat)
        if not current_player or current_player.player_id != player_id:
            raise GameError("Not your turn to bid")

        if player_id in rs.bids:
            raise GameError("Already bid this round")

        is_dealer = rs.current_player_seat == rs.dealer_seat

        if not is_valid_bid(
            bid, rs.hand_size, rs.bids, self.state.player_count,
            is_dealer, self.state.config.hook_rule,
        ):
            raise GameError("Invalid bid")

        rs.bids[player_id] = bid
        current_player.bid = bid

        # Move to next player
        if len(rs.bids) == self.state.player_count:
            # All bids placed, start playing
            rs.current_player_seat = (rs.dealer_seat + 1) % self.state.player_count
            self.state.phase = GamePhase.PLAYING
        else:
            rs.current_player_seat = (rs.current_player_seat + 1) % self.state.player_count

    def play_card(self, player_id: str, card: Card) -> TrickResult:
        if self.state.phase != GamePhase.PLAYING:
            raise GameError("Not in playing phase")

        rs = self.state.round_state
        if rs is None:
            raise GameError("No round in progress")

        current_player = self.state.get_player_by_seat(rs.current_player_seat)
        if not current_player or current_player.player_id != player_id:
            raise GameError("Not your turn to play")

        lead_suit = rs.current_trick[0].card.suit if rs.current_trick else None

        if not is_valid_play(card, current_player.hand, lead_suit):
            raise GameError("Invalid card play")

        # Remove card from hand and add to trick
        current_player.hand.remove(card)
        rs.current_trick.append(TrickCard(player_id=player_id, card=card))

        # If this is the first card, set lead suit
        if len(rs.current_trick) == 1:
            rs.lead_suit = card.suit

        # Check if trick is complete
        if len(rs.current_trick) == self.state.player_count:
            return self._complete_trick()

        # Next player
        rs.current_player_seat = (rs.current_player_seat + 1) % self.state.player_count
        return TrickResult(trick_complete=False)

    def _complete_trick(self) -> TrickResult:
        rs = self.state.round_state
        assert rs is not None

        winner_id = determine_trick_winner(rs.current_trick, rs.trump_suit)
        winner = self.state.get_player(winner_id)
        assert winner is not None
        winner.tricks_won += 1

        completed_trick = list(rs.current_trick)
        rs.tricks.append(completed_trick)
        rs.current_trick = []
        rs.lead_suit = None

        # Check if round is over
        if not any(p.hand for p in self.state.players):
            self._score_round()
            return TrickResult(
                trick_complete=True,
                winner_id=winner_id,
                trick=completed_trick,
                round_over=True,
            )

        # Winner leads next trick
        rs.current_player_seat = winner.seat_index
        return TrickResult(
            trick_complete=True,
            winner_id=winner_id,
            trick=completed_trick,
            round_over=False,
        )

    def _score_round(self) -> None:
        rs = self.state.round_state
        assert rs is not None

        round_scores: list[RoundScoreEntry] = []
        for p in self.state.players:
            assert p.bid is not None
            points = calculate_score(p.bid, p.tricks_won, self.state.config.scoring_variant)
            p.score += points
            round_scores.append(RoundScoreEntry(
                player_id=p.player_id,
                bid=p.bid,
                tricks_won=p.tricks_won,
                round_points=points,
                cumulative_score=p.score,
            ))

        self.state.scores_history.append(round_scores)

        # Advance to next round
        self.state.round_number += 1
        self.state.dealer_seat = (self.state.dealer_seat + 1) % self.state.player_count

        # Check if game is over
        if self.state.round_number >= self.state.total_rounds():
            self.state.phase = GamePhase.GAME_OVER
        else:
            self.state.phase = GamePhase.SCORING

    def advance_to_next_round(self) -> None:
        """Called after scoring display to start the next round."""
        if self.state.phase != GamePhase.SCORING:
            raise GameError("Not in scoring phase")
        self._start_round()

    def get_current_player_id(self) -> str | None:
        rs = self.state.round_state
        if rs is None:
            return None
        player = self.state.get_player_by_seat(rs.current_player_seat)
        return player.player_id if player else None

    def get_valid_cards_for_player(self, player_id: str) -> list[Card]:
        player = self.state.get_player(player_id)
        if not player:
            return []
        rs = self.state.round_state
        if rs is None:
            return []
        lead_suit = rs.current_trick[0].card.suit if rs.current_trick else None
        return get_valid_cards(player.hand, lead_suit)

    def get_valid_bids_for_player(self, player_id: str) -> list[int]:
        rs = self.state.round_state
        if rs is None:
            return []
        player = self.state.get_player(player_id)
        if not player:
            return []
        is_dealer = player.seat_index == rs.dealer_seat
        return get_valid_bids(
            rs.hand_size, rs.bids, self.state.player_count,
            is_dealer, self.state.config.hook_rule,
        )

    def get_player_view(self, player_id: str) -> dict:
        """Get game state filtered for a specific player (hides other hands)."""
        rs = self.state.round_state
        player = self.state.get_player(player_id)

        players_view = []
        for p in self.state.players:
            players_view.append({
                "id": p.player_id,
                "display_name": p.display_name,
                "seat_index": p.seat_index,
                "is_bot": p.is_bot,
                "is_connected": p.is_connected,
                "avatar_url": p.avatar_url,
                "card_count": len(p.hand),
                "bid": p.bid,
                "tricks_won": p.tricks_won,
                "score": p.score,
            })

        current_trick = []
        if rs and rs.current_trick:
            current_trick = [
                {"player_id": tc.player_id, "card": tc.card.to_dict()}
                for tc in rs.current_trick
            ]

        scores_history = []
        for round_scores in self.state.scores_history:
            scores_history.append([
                {
                    "player_id": s.player_id,
                    "bid": s.bid,
                    "tricks_won": s.tricks_won,
                    "round_points": s.round_points,
                    "cumulative_score": s.cumulative_score,
                }
                for s in round_scores
            ])

        return {
            "room_code": self.state.room_code,
            "phase": self.state.phase.value,
            "players": players_view,
            "host_id": self.state.host_id,
            "my_id": player_id,
            "hand": [c.to_dict() for c in player.hand] if player else [],
            "trump_card": rs.trump_card.to_dict() if rs and rs.trump_card else None,
            "trump_suit": rs.trump_suit.value if rs and rs.trump_suit else None,
            "current_trick": current_trick,
            "current_player_id": self.get_current_player_id(),
            "dealer_id": (
                self.state.get_player_by_seat(rs.dealer_seat).player_id
                if rs and self.state.get_player_by_seat(rs.dealer_seat)
                else None
            ),
            "round_number": self.state.round_number + 1,  # 1-indexed for display
            "hand_size": rs.hand_size if rs else 0,
            "total_rounds": self.state.total_rounds(),
            "valid_cards": (
                [c.to_dict() for c in self.get_valid_cards_for_player(player_id)]
                if self.state.phase == GamePhase.PLAYING
                and self.get_current_player_id() == player_id
                else []
            ),
            "valid_bids": (
                self.get_valid_bids_for_player(player_id)
                if self.state.phase == GamePhase.BIDDING
                and self.get_current_player_id() == player_id
                else []
            ),
            "scores_history": scores_history,
            "config": self.state.config.to_dict(),
        }

    def get_winner(self) -> PlayerState | None:
        if self.state.phase not in (GamePhase.GAME_OVER, GamePhase.FINISHED):
            return None
        if not self.state.players:
            return None
        return max(self.state.players, key=lambda p: p.score)

    def set_player_connected(self, player_id: str, connected: bool) -> None:
        player = self.state.get_player(player_id)
        if player:
            player.is_connected = connected


class TrickResult:
    def __init__(
        self,
        trick_complete: bool,
        winner_id: str | None = None,
        trick: list[TrickCard] | None = None,
        round_over: bool = False,
    ):
        self.trick_complete = trick_complete
        self.winner_id = winner_id
        self.trick = trick or []
        self.round_over = round_over
