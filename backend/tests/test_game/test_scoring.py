from app.game.scoring import calculate_score
from app.game.types import ScoringVariant


class TestStandardScoring:
    def test_exact_bid_zero(self):
        assert calculate_score(0, 0, ScoringVariant.STANDARD) == 10

    def test_exact_bid_nonzero(self):
        assert calculate_score(3, 3, ScoringVariant.STANDARD) == 13

    def test_overbid(self):
        assert calculate_score(3, 1, ScoringVariant.STANDARD) == 0

    def test_underbid(self):
        assert calculate_score(1, 3, ScoringVariant.STANDARD) == 0

    def test_exact_bid_one(self):
        assert calculate_score(1, 1, ScoringVariant.STANDARD) == 11


class TestProgressiveScoring:
    def test_exact_bid_zero(self):
        assert calculate_score(0, 0, ScoringVariant.PROGRESSIVE) == 10

    def test_exact_bid_nonzero(self):
        assert calculate_score(3, 3, ScoringVariant.PROGRESSIVE) == 19  # 10 + 9

    def test_overbid(self):
        assert calculate_score(3, 1, ScoringVariant.PROGRESSIVE) == -2

    def test_underbid(self):
        assert calculate_score(1, 3, ScoringVariant.PROGRESSIVE) == -2

    def test_exact_bid_one(self):
        assert calculate_score(1, 1, ScoringVariant.PROGRESSIVE) == 11


class TestBasicScoring:
    def test_exact_bid_zero(self):
        assert calculate_score(0, 0, ScoringVariant.BASIC) == 10

    def test_exact_bid_nonzero(self):
        assert calculate_score(3, 3, ScoringVariant.BASIC) == 13  # 3 + 10

    def test_overbid(self):
        assert calculate_score(3, 1, ScoringVariant.BASIC) == 1  # just tricks

    def test_underbid(self):
        assert calculate_score(1, 3, ScoringVariant.BASIC) == 3  # just tricks

    def test_zero_bid_miss(self):
        assert calculate_score(0, 2, ScoringVariant.BASIC) == 2
