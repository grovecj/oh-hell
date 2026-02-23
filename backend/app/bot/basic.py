from __future__ import annotations

import random

from app.bot.strategy import BotStrategy
from app.game.types import Card, GameState, PlayerState, Rank


class BasicBot(BotStrategy):
    """Basic heuristic bot: count high cards for bids, play simple strategy."""

    def choose_bid(self, player: PlayerState, state: GameState, valid_bids: list[int]) -> int:
        if not valid_bids:
            return 0

        trump_suit = state.round_state.trump_suit if state.round_state else None

        # Count likely winners: high trump cards and aces
        expected_wins = 0
        for card in player.hand:
            if trump_suit and card.suit == trump_suit:
                if card.rank.value_order >= Rank.JACK.value_order:
                    expected_wins += 1
                elif card.rank.value_order >= Rank.NINE.value_order:
                    expected_wins += 0.5
            elif card.rank == Rank.ACE:
                expected_wins += 0.7

        bid = round(expected_wins)
        bid = max(0, min(bid, state.round_state.hand_size if state.round_state else 0))

        # Pick closest valid bid
        if bid in valid_bids:
            return bid
        return min(valid_bids, key=lambda b: abs(b - bid))

    def choose_card(self, player: PlayerState, state: GameState, valid_cards: list[Card]) -> Card:
        if not valid_cards:
            raise ValueError("No valid cards")
        if len(valid_cards) == 1:
            return valid_cards[0]

        tricks_needed = (player.bid or 0) - player.tricks_won

        if tricks_needed > 0:
            # Try to win: play highest card
            return max(valid_cards, key=lambda c: self._card_strength(c, state))
        else:
            # Try to lose: play lowest card
            return min(valid_cards, key=lambda c: self._card_strength(c, state))

    def _card_strength(self, card: Card, state: GameState) -> int:
        trump_suit = state.round_state.trump_suit if state.round_state else None
        base = card.rank.value_order
        if trump_suit and card.suit == trump_suit:
            base += 20  # Trump cards are stronger
        return base
