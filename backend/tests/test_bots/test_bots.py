import random

import pytest

from app.bot.basic import BasicBot
from app.bot.intermediate import IntermediateBot
from app.game.engine import GameEngine
from app.game.types import GameConfig, GamePhase


def play_full_game_with_bots(bot_class, num_players=4, seed=42):
    """Play a complete game using the given bot class for all players."""
    config = GameConfig(hook_rule=False)
    engine = GameEngine(room_code="BOT_TEST", config=config)
    engine._rng = random.Random(seed)

    bots = {}
    for i in range(num_players):
        pid = f"bot_{i}"
        engine.add_player(pid, f"Bot {i}", is_bot=True)
        bots[pid] = bot_class()

    engine.start_game(f"bot_0")

    max_iterations = 10000
    iterations = 0

    while engine.phase not in (GamePhase.GAME_OVER, GamePhase.FINISHED):
        iterations += 1
        if iterations > max_iterations:
            pytest.fail(f"Game did not finish after {max_iterations} iterations, phase={engine.phase}")

        if engine.phase == GamePhase.SCORING:
            engine.advance_to_next_round()
            continue

        current_id = engine.get_current_player_id()
        if not current_id:
            break

        player = engine.state.get_player(current_id)
        bot = bots[current_id]

        if engine.phase == GamePhase.BIDDING:
            valid_bids = engine.get_valid_bids_for_player(current_id)
            bid = bot.choose_bid(player, engine.state, valid_bids)
            assert bid in valid_bids, f"Bot bid {bid} not in valid bids {valid_bids}"
            engine.place_bid(current_id, bid)

        elif engine.phase == GamePhase.PLAYING:
            valid_cards = engine.get_valid_cards_for_player(current_id)
            card = bot.choose_card(player, engine.state, valid_cards)
            assert card in valid_cards, f"Bot played {card} not in valid cards"
            engine.play_card(current_id, card)

    return engine


class TestBasicBot:
    def test_plays_full_game_3p(self):
        engine = play_full_game_with_bots(BasicBot, 3)
        assert engine.phase == GamePhase.GAME_OVER

    def test_plays_full_game_4p(self):
        engine = play_full_game_with_bots(BasicBot, 4)
        assert engine.phase == GamePhase.GAME_OVER

    def test_plays_full_game_7p(self):
        engine = play_full_game_with_bots(BasicBot, 7)
        assert engine.phase == GamePhase.GAME_OVER

    def test_different_seeds_different_outcomes(self):
        e1 = play_full_game_with_bots(BasicBot, 4, seed=1)
        e2 = play_full_game_with_bots(BasicBot, 4, seed=2)
        scores1 = [p.score for p in e1.players]
        scores2 = [p.score for p in e2.players]
        # Different seeds should produce different results
        assert scores1 != scores2

    def test_scores_are_reasonable(self):
        engine = play_full_game_with_bots(BasicBot, 4, seed=100)
        for p in engine.players:
            assert p.score >= 0, f"Player {p.display_name} has negative score"


class TestIntermediateBot:
    def test_plays_full_game_3p(self):
        engine = play_full_game_with_bots(IntermediateBot, 3)
        assert engine.phase == GamePhase.GAME_OVER

    def test_plays_full_game_4p(self):
        engine = play_full_game_with_bots(IntermediateBot, 4)
        assert engine.phase == GamePhase.GAME_OVER

    def test_plays_full_game_7p(self):
        engine = play_full_game_with_bots(IntermediateBot, 7)
        assert engine.phase == GamePhase.GAME_OVER

    def test_multiple_seeds(self):
        """Run with multiple seeds to ensure robustness."""
        for seed in range(10):
            engine = play_full_game_with_bots(IntermediateBot, 4, seed=seed)
            assert engine.phase == GamePhase.GAME_OVER, f"Failed with seed {seed}"


class TestMixedBots:
    def test_basic_vs_intermediate(self):
        """Play a game with mixed bot types."""
        config = GameConfig(hook_rule=True)
        engine = GameEngine(room_code="MIX_TEST", config=config)
        engine._rng = random.Random(42)

        bots = {}
        for i in range(4):
            pid = f"bot_{i}"
            engine.add_player(pid, f"Bot {i}", is_bot=True)
            bots[pid] = BasicBot() if i < 2 else IntermediateBot()

        engine.start_game("bot_0")

        max_iterations = 10000
        iterations = 0

        while engine.phase not in (GamePhase.GAME_OVER, GamePhase.FINISHED):
            iterations += 1
            if iterations > max_iterations:
                break

            if engine.phase == GamePhase.SCORING:
                engine.advance_to_next_round()
                continue

            current_id = engine.get_current_player_id()
            if not current_id:
                break

            player = engine.state.get_player(current_id)
            bot = bots[current_id]

            if engine.phase == GamePhase.BIDDING:
                valid_bids = engine.get_valid_bids_for_player(current_id)
                bid = bot.choose_bid(player, engine.state, valid_bids)
                engine.place_bid(current_id, bid)
            elif engine.phase == GamePhase.PLAYING:
                valid_cards = engine.get_valid_cards_for_player(current_id)
                card = bot.choose_card(player, engine.state, valid_cards)
                engine.play_card(current_id, card)

        assert engine.phase == GamePhase.GAME_OVER
