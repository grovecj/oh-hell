from app.game.types import ScoringVariant


def calculate_score(
    bid: int,
    tricks_won: int,
    variant: ScoringVariant,
) -> int:
    if variant == ScoringVariant.STANDARD:
        if tricks_won == bid:
            return 10 + bid
        return 0

    if variant == ScoringVariant.PROGRESSIVE:
        if tricks_won == bid:
            return 10 + bid * bid
        return -abs(tricks_won - bid)

    if variant == ScoringVariant.BASIC:
        bonus = 10 if tricks_won == bid else 0
        return tricks_won + bonus

    raise ValueError(f"Unknown scoring variant: {variant}")
