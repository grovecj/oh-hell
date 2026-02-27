import random

import pytest

from app.game.engine import GameEngine, GameError
from app.game.types import GameConfig, GamePhase


def make_engine(num_players=3, config=None) -> GameEngine:
    engine = GameEngine(room_code="TEST01", config=config)
    for i in range(num_players):
        engine.add_player(f"p{i+1}", f"Player {i+1}")
    return engine


class TestAddRemovePlayer:
    def test_add_player(self):
        engine = GameEngine(room_code="TEST01")
        p = engine.add_player("p1", "Alice")
        assert p.player_id == "p1"
        assert p.display_name == "Alice"
        assert p.seat_index == 0

    def test_first_player_is_host(self):
        engine = GameEngine(room_code="TEST01")
        engine.add_player("p1", "Alice")
        assert engine.state.host_id == "p1"

    def test_add_multiple_players(self):
        engine = GameEngine(room_code="TEST01")
        engine.add_player("p1", "Alice")
        engine.add_player("p2", "Bob")
        assert len(engine.players) == 2
        assert engine.players[1].seat_index == 1

    def test_cannot_add_duplicate(self):
        engine = GameEngine(room_code="TEST01")
        engine.add_player("p1", "Alice")
        with pytest.raises(GameError):
            engine.add_player("p1", "Alice")

    def test_cannot_add_when_full(self):
        config = GameConfig(max_players=3)
        engine = GameEngine(room_code="TEST01", config=config)
        engine.add_player("p1", "A")
        engine.add_player("p2", "B")
        engine.add_player("p3", "C")
        with pytest.raises(GameError):
            engine.add_player("p4", "D")

    def test_remove_player(self):
        engine = GameEngine(room_code="TEST01")
        engine.add_player("p1", "Alice")
        engine.add_player("p2", "Bob")
        engine.remove_player("p2")
        assert len(engine.players) == 1

    def test_remove_host_reassigns(self):
        engine = GameEngine(room_code="TEST01")
        engine.add_player("p1", "Alice")
        engine.add_player("p2", "Bob")
        engine.remove_player("p1")
        assert engine.state.host_id == "p2"

    def test_remove_reseats(self):
        engine = GameEngine(room_code="TEST01")
        engine.add_player("p1", "A")
        engine.add_player("p2", "B")
        engine.add_player("p3", "C")
        engine.remove_player("p2")
        assert engine.players[0].seat_index == 0
        assert engine.players[1].seat_index == 1

    def test_cannot_add_after_start(self):
        engine = make_engine(3)
        engine.start_game("p1")
        with pytest.raises(GameError):
            engine.add_player("p4", "D")


class TestStartGame:
    def test_start_game(self):
        engine = make_engine(3)
        engine.start_game("p1")
        assert engine.phase == GamePhase.BIDDING

    def test_cannot_start_with_2_players(self):
        engine = GameEngine(room_code="TEST01")
        engine.add_player("p1", "A")
        engine.add_player("p2", "B")
        with pytest.raises(GameError):
            engine.start_game("p1")

    def test_non_host_cannot_start(self):
        engine = make_engine(3)
        with pytest.raises(GameError):
            engine.start_game("p2")

    def test_all_players_dealt_cards(self):
        engine = make_engine(3)
        engine.start_game("p1")
        for p in engine.players:
            assert len(p.hand) == 1  # First round, 3 players

    def test_trump_card_set(self):
        engine = make_engine(3)
        engine.start_game("p1")
        assert engine.state.round_state is not None
        assert engine.state.round_state.trump_card is not None


class TestRoundSequence:
    def test_3_players(self):
        engine = make_engine(3)
        seq = engine.state.round_sequence()
        max_h = 52 // 3  # 17
        assert seq[0] == 1
        assert max(seq) == max_h
        assert seq[-1] == 1
        assert len(seq) == max_h * 2 - 1

    def test_4_players(self):
        engine = make_engine(4)
        seq = engine.state.round_sequence()
        assert max(seq) == 13
        assert len(seq) == 25  # 1..13..1

    def test_7_players(self):
        engine = make_engine(7)
        max_h = 52 // 7  # 7
        seq = engine.state.round_sequence()
        assert max(seq) == max_h


class TestBidding:
    def test_bid_order_starts_left_of_dealer(self):
        engine = make_engine(3)
        engine.start_game("p1")
        # Dealer is seat 0 (p1), so first bidder is seat 1 (p2)
        assert engine.get_current_player_id() == "p2"

    def test_place_bid(self):
        engine = make_engine(3)
        engine.start_game("p1")
        engine.place_bid("p2", 0)
        assert engine.state.round_state.bids["p2"] == 0

    def test_bidding_advances_player(self):
        engine = make_engine(3)
        engine.start_game("p1")
        engine.place_bid("p2", 0)
        assert engine.get_current_player_id() == "p3"

    def test_all_bids_transitions_to_playing(self):
        engine = make_engine(3)
        engine.start_game("p1")
        engine.place_bid("p2", 0)
        engine.place_bid("p3", 0)
        engine.place_bid("p1", 0)  # Dealer bids last
        assert engine.phase == GamePhase.PLAYING

    def test_wrong_player_cannot_bid(self):
        engine = make_engine(3)
        engine.start_game("p1")
        with pytest.raises(GameError):
            engine.place_bid("p1", 0)  # Not p1's turn (p2 goes first)

    def test_invalid_bid_rejected(self):
        engine = make_engine(3)
        engine.start_game("p1")
        with pytest.raises(GameError):
            engine.place_bid("p2", 5)  # hand_size is 1, max bid is 1


class TestPlayCard:
    def _setup_playing_engine(self):
        """Set up an engine in the PLAYING phase with known cards."""
        engine = make_engine(3)
        engine._rng = random.Random(42)
        engine.start_game("p1")
        # Place bids for all players
        for _ in range(3):
            pid = engine.get_current_player_id()
            engine.place_bid(pid, 0)
        assert engine.phase == GamePhase.PLAYING
        return engine

    def test_play_card_removes_from_hand(self):
        engine = self._setup_playing_engine()
        pid = engine.get_current_player_id()
        player = engine.state.get_player(pid)
        card = player.hand[0]
        engine.play_card(pid, card)
        assert card not in player.hand

    def test_play_card_adds_to_trick(self):
        engine = self._setup_playing_engine()
        pid = engine.get_current_player_id()
        player = engine.state.get_player(pid)
        card = player.hand[0]
        engine.play_card(pid, card)
        assert len(engine.state.round_state.current_trick) == 1

    def test_wrong_player_cannot_play(self):
        engine = self._setup_playing_engine()
        pid = engine.get_current_player_id()
        # Find a different player
        other = [p for p in engine.players if p.player_id != pid][0]
        with pytest.raises(GameError):
            engine.play_card(other.player_id, other.hand[0])

    def test_trick_completes_after_all_play(self):
        engine = self._setup_playing_engine()
        # All play their only card (hand_size = 1)
        for _ in range(3):
            pid = engine.get_current_player_id()
            player = engine.state.get_player(pid)
            result = engine.play_card(pid, player.hand[0])
        assert result.trick_complete
        assert result.round_over  # hand_size 1, only 1 trick


class TestFullRound:
    def test_scoring_after_round(self):
        engine = make_engine(3)
        engine._rng = random.Random(42)
        engine.start_game("p1")

        # Bid 0 for everyone
        for _ in range(3):
            pid = engine.get_current_player_id()
            engine.place_bid(pid, 0)

        # Play cards
        for _ in range(3):
            pid = engine.get_current_player_id()
            player = engine.state.get_player(pid)
            engine.play_card(pid, player.hand[0])

        # Should have scored
        assert len(engine.state.scores_history) == 1

    def test_multiple_rounds(self):
        """Play through first 2 rounds of a 3-player game."""
        engine = make_engine(3)
        engine._rng = random.Random(42)
        engine.start_game("p1")

        for _round_num in range(2):
            # Bid phase
            for _ in range(3):
                pid = engine.get_current_player_id()
                valid_bids = engine.get_valid_bids_for_player(pid)
                engine.place_bid(pid, valid_bids[0])

            # Play phase
            hand_size = engine.state.round_state.hand_size
            for _trick in range(hand_size):
                for _ in range(3):
                    pid = engine.get_current_player_id()
                    valid = engine.get_valid_cards_for_player(pid)
                    engine.play_card(pid, valid[0])

            if engine.phase == GamePhase.SCORING:
                engine.advance_to_next_round()

        assert engine.state.round_number >= 2


class TestPlayerView:
    def test_view_hides_other_hands(self):
        engine = make_engine(3)
        engine._rng = random.Random(42)
        engine.start_game("p1")
        view = engine.get_player_view("p1")
        # p1's hand is visible
        assert len(view["hand"]) > 0
        # Other players show card_count but not actual cards
        for p in view["players"]:
            if p["id"] != "p1":
                assert "hand" not in p or p.get("hand") is None
                assert p["card_count"] >= 0

    def test_view_shows_valid_actions(self):
        engine = make_engine(3)
        engine._rng = random.Random(42)
        engine.start_game("p1")
        # p2 should see valid bids (they bid first)
        view = engine.get_player_view("p2")
        assert len(view["valid_bids"]) > 0
        # p1 should not see valid bids (not their turn)
        view = engine.get_player_view("p1")
        assert len(view["valid_bids"]) == 0


class TestGameOver:
    def test_game_ends_after_all_rounds(self):
        """Play a quick game with 3 players to verify game over."""
        config = GameConfig(hook_rule=False)
        engine = GameEngine(room_code="TEST01", config=config)
        for i in range(3):
            engine.add_player(f"p{i+1}", f"Player {i+1}")
        engine._rng = random.Random(42)
        engine.start_game("p1")

        rounds_played = 0
        max_rounds = engine.state.total_rounds()

        while engine.phase not in (GamePhase.GAME_OVER, GamePhase.FINISHED):
            if engine.phase == GamePhase.BIDDING:
                for _ in range(3):
                    pid = engine.get_current_player_id()
                    valid = engine.get_valid_bids_for_player(pid)
                    engine.place_bid(pid, valid[0])
            elif engine.phase == GamePhase.PLAYING:
                while engine.phase == GamePhase.PLAYING:
                    pid = engine.get_current_player_id()
                    valid = engine.get_valid_cards_for_player(pid)
                    engine.play_card(pid, valid[0])
            elif engine.phase == GamePhase.SCORING:
                rounds_played += 1
                engine.advance_to_next_round()

            if rounds_played > max_rounds + 1:
                break

        assert engine.phase == GamePhase.GAME_OVER
        assert engine.get_winner() is not None
