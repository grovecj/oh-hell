import random

from app.game.types import Card, Rank, Suit


def create_deck() -> list[Card]:
    return [Card(suit=s, rank=r) for s in Suit for r in Rank]


def shuffle_deck(deck: list[Card], rng: random.Random | None = None) -> list[Card]:
    shuffled = deck.copy()
    if rng:
        rng.shuffle(shuffled)
    else:
        random.shuffle(shuffled)
    return shuffled


def deal(deck: list[Card], num_players: int, cards_per_player: int) -> tuple[list[list[Card]], Card | None]:
    """Deal cards from the deck.

    Returns (hands, trump_card). trump_card is the next card after dealing,
    or None if no cards remain.
    """
    hands: list[list[Card]] = [[] for _ in range(num_players)]
    idx = 0
    for _ in range(cards_per_player):
        for p in range(num_players):
            hands[p].append(deck[idx])
            idx += 1

    trump_card = deck[idx] if idx < len(deck) else None
    return hands, trump_card
