from __future__ import annotations

from app.bot.strategy import BotStrategy
from app.game.types import Card, GameState, PlayerState, Rank, Suit


class IntermediateBot(BotStrategy):
    """Intermediate bot with card counting, void detection, and positional play."""

    def __init__(self):
        self._played_cards: set[tuple[str, str]] = set()

    def _track_played_cards(self, state: GameState):
        """Rebuild set of played cards from round state."""
        self._played_cards.clear()
        rs = state.round_state
        if not rs:
            return
        for trick in rs.tricks:
            for tc in trick:
                self._played_cards.add((tc.card.suit.value, tc.card.rank.value))
        for tc in rs.current_trick:
            self._played_cards.add((tc.card.suit.value, tc.card.rank.value))

    def _cards_remaining_in_suit(self, suit: Suit, excluding_hand: list[Card]) -> int:
        """Count unseen cards of a suit (not in hand, not played)."""
        total = 13
        played_in_suit = sum(1 for s, r in self._played_cards if s == suit.value)
        in_hand = sum(1 for c in excluding_hand if c.suit == suit)
        return total - played_in_suit - in_hand

    def _is_highest_remaining(self, card: Card, hand: list[Card]) -> bool:
        """Check if this card is the highest remaining of its suit."""
        for rank in reversed(list(Rank)):
            if rank == card.rank:
                return True
            key = (card.suit.value, rank.value)
            if key not in self._played_cards and not any(
                c.suit == card.suit and c.rank == rank for c in hand
            ):
                return False
        return True

    def choose_bid(self, player: PlayerState, state: GameState, valid_bids: list[int]) -> int:
        if not valid_bids:
            return 0

        self._track_played_cards(state)
        trump_suit = state.round_state.trump_suit if state.round_state else None

        expected_wins = 0.0
        hand = player.hand

        for card in hand:
            if trump_suit and card.suit == trump_suit:
                # High trump is very likely to win
                if card.rank.value_order >= Rank.QUEEN.value_order:
                    expected_wins += 0.9
                elif card.rank.value_order >= Rank.TEN.value_order:
                    expected_wins += 0.7
                elif card.rank.value_order >= Rank.SEVEN.value_order:
                    expected_wins += 0.4
                else:
                    expected_wins += 0.2
            else:
                # Non-trump high cards
                if card.rank == Rank.ACE:
                    # Ace wins unless trumped; factor in how many trump remain
                    trump_remaining = (
                        self._cards_remaining_in_suit(trump_suit, hand)
                        if trump_suit else 0
                    )
                    void_chance = 1.0 - (trump_remaining / 13.0) if trump_remaining > 0 else 1.0
                    expected_wins += 0.6 * void_chance + 0.3
                elif card.rank == Rank.KING:
                    expected_wins += 0.35
                elif card.rank == Rank.QUEEN:
                    expected_wins += 0.15

        # Adjust for position (later positions have slight advantage)
        position_bonus = player.seat_index * 0.05

        bid = round(expected_wins + position_bonus)
        hand_size = state.round_state.hand_size if state.round_state else 1
        bid = max(0, min(bid, hand_size))

        if bid in valid_bids:
            return bid
        return min(valid_bids, key=lambda b: abs(b - bid))

    def choose_card(self, player: PlayerState, state: GameState, valid_cards: list[Card]) -> Card:
        if not valid_cards:
            raise ValueError("No valid cards")
        if len(valid_cards) == 1:
            return valid_cards[0]

        self._track_played_cards(state)

        rs = state.round_state
        trump_suit = rs.trump_suit if rs else None
        tricks_needed = (player.bid or 0) - player.tricks_won
        is_leading = not rs.current_trick if rs else True

        if is_leading:
            return self._choose_lead(player, state, valid_cards, tricks_needed, trump_suit)
        else:
            return self._choose_follow(player, state, valid_cards, tricks_needed, trump_suit)

    def _choose_lead(
        self, player: PlayerState, state: GameState, valid_cards: list[Card],
        tricks_needed: int, trump_suit: Suit | None,
    ) -> Card:
        if tricks_needed > 0:
            # Lead with strongest card — prefer guaranteed winners
            for card in sorted(
                valid_cards,
                key=lambda c: self._card_strength(c, trump_suit),
                reverse=True,
            ):
                if self._is_highest_remaining(card, player.hand):
                    return card
            return max(valid_cards, key=lambda c: self._card_strength(c, trump_suit))
        else:
            # Lead with weakest to avoid winning
            non_trump = [c for c in valid_cards if not trump_suit or c.suit != trump_suit]
            candidates = non_trump if non_trump else valid_cards
            return min(candidates, key=lambda c: self._card_strength(c, trump_suit))

    def _choose_follow(
        self, player: PlayerState, state: GameState, valid_cards: list[Card],
        tricks_needed: int, trump_suit: Suit | None,
    ) -> Card:
        rs = state.round_state
        if not rs or not rs.current_trick:
            return valid_cards[0]

        # Evaluate current trick winner
        current_winning_strength = max(
            self._card_strength(tc.card, trump_suit) for tc in rs.current_trick
        )

        if tricks_needed > 0:
            # Try to win: play lowest card that beats current winner
            winners = [
                c for c in valid_cards
                if self._card_strength(c, trump_suit) > current_winning_strength
            ]
            if winners:
                return min(winners, key=lambda c: self._card_strength(c, trump_suit))
            # Can't win — dump lowest
            return min(valid_cards, key=lambda c: self._card_strength(c, trump_suit))
        else:
            # Try not to win: play highest card that doesn't beat current winner
            losers = [
                c for c in valid_cards
                if self._card_strength(c, trump_suit) <= current_winning_strength
            ]
            if losers:
                return max(losers, key=lambda c: self._card_strength(c, trump_suit))
            # All cards would win — play lowest
            return min(valid_cards, key=lambda c: self._card_strength(c, trump_suit))

    def _card_strength(self, card: Card, trump_suit: Suit | None) -> int:
        base = card.rank.value_order
        if trump_suit and card.suit == trump_suit:
            base += 20
        return base
