import random

from app.game.deck import create_deck, deal, shuffle_deck
from app.game.types import Card, Rank, Suit


def test_create_deck_has_52_cards():
    deck = create_deck()
    assert len(deck) == 52


def test_create_deck_all_unique():
    deck = create_deck()
    assert len(set(deck)) == 52


def test_create_deck_has_all_suits():
    deck = create_deck()
    suits = {c.suit for c in deck}
    assert suits == {Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES}


def test_create_deck_has_13_per_suit():
    deck = create_deck()
    for suit in Suit:
        assert sum(1 for c in deck if c.suit == suit) == 13


def test_shuffle_deck_deterministic():
    deck = create_deck()
    rng = random.Random(42)
    shuffled1 = shuffle_deck(deck, rng)
    rng = random.Random(42)
    shuffled2 = shuffle_deck(deck, rng)
    assert shuffled1 == shuffled2


def test_shuffle_deck_changes_order():
    deck = create_deck()
    shuffled = shuffle_deck(deck, random.Random(42))
    assert shuffled != deck  # Extremely unlikely to be same order


def test_deal_correct_hand_sizes():
    deck = create_deck()
    hands, trump = deal(deck, 4, 5)
    assert len(hands) == 4
    for hand in hands:
        assert len(hand) == 5


def test_deal_returns_trump_card():
    deck = create_deck()
    hands, trump = deal(deck, 4, 5)
    assert trump is not None
    # Trump should be card at index 20 (4*5)
    assert trump == deck[20]


def test_deal_no_trump_when_all_cards_used():
    deck = create_deck()
    hands, trump = deal(deck, 4, 13)
    assert trump is None


def test_deal_no_duplicate_cards():
    deck = shuffle_deck(create_deck(), random.Random(42))
    hands, trump = deal(deck, 4, 7)
    all_cards = [c for hand in hands for c in hand]
    if trump:
        all_cards.append(trump)
    assert len(all_cards) == len(set(all_cards))
