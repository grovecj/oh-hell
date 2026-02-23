from app.game.types import Card, Rank, Suit, TrickCard


def get_valid_cards(hand: list[Card], lead_suit: Suit | None) -> list[Card]:
    """Return the cards in hand that are legal to play.

    If there's a lead suit and the player has cards of that suit, they must follow suit.
    Otherwise, any card is valid.
    """
    if lead_suit is None:
        return list(hand)

    suited = [c for c in hand if c.suit == lead_suit]
    if suited:
        return suited
    return list(hand)


def is_valid_play(card: Card, hand: list[Card], lead_suit: Suit | None) -> bool:
    if card not in hand:
        return False
    valid = get_valid_cards(hand, lead_suit)
    return card in valid


def get_valid_bids(
    hand_size: int,
    bids_so_far: dict[str, int],
    player_count: int,
    is_dealer: bool,
    hook_rule: bool,
) -> list[int]:
    """Return valid bids for the current player.

    Hook rule: if the player is the dealer and the hook rule is enabled,
    they cannot bid a number that would make total bids == hand_size.
    """
    all_bids = list(range(0, hand_size + 1))

    if is_dealer and hook_rule and len(bids_so_far) == player_count - 1:
        current_total = sum(bids_so_far.values())
        forbidden = hand_size - current_total
        if 0 <= forbidden <= hand_size:
            all_bids = [b for b in all_bids if b != forbidden]

    return all_bids


def is_valid_bid(
    bid: int,
    hand_size: int,
    bids_so_far: dict[str, int],
    player_count: int,
    is_dealer: bool,
    hook_rule: bool,
) -> bool:
    return bid in get_valid_bids(hand_size, bids_so_far, player_count, is_dealer, hook_rule)


def determine_trick_winner(trick: list[TrickCard], trump_suit: Suit | None) -> str:
    """Determine which player wins the trick.

    Highest trump wins. If no trump played, highest of lead suit wins.
    """
    if not trick:
        raise ValueError("Empty trick")

    lead_suit = trick[0].card.suit

    trump_cards = [(tc, tc.card.rank.value_order) for tc in trick if trump_suit and tc.card.suit == trump_suit]
    if trump_cards:
        winner = max(trump_cards, key=lambda x: x[1])
        return winner[0].player_id

    lead_cards = [(tc, tc.card.rank.value_order) for tc in trick if tc.card.suit == lead_suit]
    winner = max(lead_cards, key=lambda x: x[1])
    return winner[0].player_id
