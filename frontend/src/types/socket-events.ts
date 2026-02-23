import type { Card, GameConfig, GameState, PlayerInfo, RoundScore, TrickCard } from './game';

// Client → Server events
export interface ClientEvents {
  join_game: { room_code: string };
  leave_game: Record<string, never>;
  start_game: Record<string, never>;
  place_bid: { bid: number };
  play_card: { card: Card };
  add_bot: { difficulty: 'basic' | 'intermediate' };
  remove_bot: { player_id: string };
  update_config: { config: Partial<GameConfig> };
  send_chat: { message: string };
}

// Server → Client events
export interface ServerEvents {
  game_state: GameState;
  cards_dealt: { hand: Card[]; trump_card: Card | null; trump_suit: string | null; hand_size: number; round_number: number };
  your_turn: { valid_cards: Card[]; time_remaining: number };
  player_joined: { player: PlayerInfo };
  player_left: { player_id: string };
  player_reconnected: { player_id: string };
  bid_placed: { player_id: string; bid: number };
  card_played: { player_id: string; card: Card };
  trick_won: { winner_id: string; trick: TrickCard[] };
  round_scored: { scores: RoundScore[]; round_number: number };
  game_over: { final_scores: RoundScore[]; winner_id: string };
  chat_message: { player_id: string; display_name: string; message: string };
  error: { message: string };
}
