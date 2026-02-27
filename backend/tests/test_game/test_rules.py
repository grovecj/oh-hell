from app.game.rules import (
    determine_trick_winner,
    get_valid_bids,
    get_valid_cards,
    is_valid_play,
)
from app.game.types import Card, Rank, Suit, TrickCard


class TestGetValidCards:
    def test_no_lead_suit_all_valid(self):
        hand = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.TWO),
            Card(Suit.SPADES, Rank.KING),
        ]
        valid = get_valid_cards(hand, None)
        assert valid == hand

    def test_must_follow_suit(self):
        hand = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.TWO),
            Card(Suit.HEARTS, Rank.THREE),
        ]
        valid = get_valid_cards(hand, Suit.HEARTS)
        assert len(valid) == 2
        assert all(c.suit == Suit.HEARTS for c in valid)

    def test_no_matching_suit_all_valid(self):
        hand = [
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.SPADES, Rank.TWO),
        ]
        valid = get_valid_cards(hand, Suit.HEARTS)
        assert valid == hand


class TestIsValidPlay:
    def test_card_not_in_hand(self):
        hand = [Card(Suit.HEARTS, Rank.ACE)]
        assert not is_valid_play(Card(Suit.CLUBS, Rank.ACE), hand, None)

    def test_valid_play_no_lead(self):
        card = Card(Suit.HEARTS, Rank.ACE)
        assert is_valid_play(card, [card], None)

    def test_must_follow_suit(self):
        hand = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.TWO),
        ]
        assert not is_valid_play(Card(Suit.CLUBS, Rank.TWO), hand, Suit.HEARTS)
        assert is_valid_play(Card(Suit.HEARTS, Rank.ACE), hand, Suit.HEARTS)


class TestGetValidBids:
    def test_all_bids_available(self):
        bids = get_valid_bids(5, {}, 4, False, True)
        assert bids == [0, 1, 2, 3, 4, 5]

    def test_hook_rule_forbids_bid(self):
        # 3 players, hand_size 3, bids so far sum to 2 -> dealer can't bid 1
        bids_so_far = {"p1": 1, "p2": 1}
        valid = get_valid_bids(3, bids_so_far, 3, True, True)
        assert 1 not in valid
        assert 0 in valid
        assert 2 in valid

    def test_hook_rule_disabled(self):
        bids_so_far = {"p1": 1, "p2": 1}
        valid = get_valid_bids(3, bids_so_far, 3, True, False)
        assert 1 in valid  # Would be forbidden with hook rule

    def test_non_dealer_not_affected_by_hook(self):
        bids_so_far = {"p1": 1}
        valid = get_valid_bids(3, bids_so_far, 3, False, True)
        assert valid == [0, 1, 2, 3]

    def test_hook_rule_forbidden_bid_zero(self):
        # All others bid 3 total for hand_size 3 -> dealer can't bid 0
        bids_so_far = {"p1": 2, "p2": 1}
        valid = get_valid_bids(3, bids_so_far, 3, True, True)
        assert 0 not in valid


class TestDetermineTrickWinner:
    def test_highest_of_lead_suit_wins(self):
        trick = [
            TrickCard("p1", Card(Suit.HEARTS, Rank.FIVE)),
            TrickCard("p2", Card(Suit.HEARTS, Rank.KING)),
            TrickCard("p3", Card(Suit.HEARTS, Rank.TWO)),
        ]
        assert determine_trick_winner(trick, None) == "p2"

    def test_trump_beats_lead_suit(self):
        trick = [
            TrickCard("p1", Card(Suit.HEARTS, Rank.ACE)),
            TrickCard("p2", Card(Suit.SPADES, Rank.TWO)),  # trump
            TrickCard("p3", Card(Suit.HEARTS, Rank.KING)),
        ]
        assert determine_trick_winner(trick, Suit.SPADES) == "p2"

    def test_highest_trump_wins(self):
        trick = [
            TrickCard("p1", Card(Suit.HEARTS, Rank.ACE)),
            TrickCard("p2", Card(Suit.SPADES, Rank.TWO)),  # trump
            TrickCard("p3", Card(Suit.SPADES, Rank.KING)),  # higher trump
        ]
        assert determine_trick_winner(trick, Suit.SPADES) == "p3"

    def test_off_suit_non_trump_loses(self):
        trick = [
            TrickCard("p1", Card(Suit.HEARTS, Rank.TWO)),
            TrickCard("p2", Card(Suit.CLUBS, Rank.ACE)),  # off-suit, not trump
            TrickCard("p3", Card(Suit.HEARTS, Rank.THREE)),
        ]
        assert determine_trick_winner(trick, Suit.SPADES) == "p3"

    def test_ace_highest(self):
        trick = [
            TrickCard("p1", Card(Suit.HEARTS, Rank.KING)),
            TrickCard("p2", Card(Suit.HEARTS, Rank.ACE)),
        ]
        assert determine_trick_winner(trick, None) == "p2"
