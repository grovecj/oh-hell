export type Suit = 'hearts' | 'diamonds' | 'clubs' | 'spades';
export type Rank = '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10' | 'J' | 'Q' | 'K' | 'A';

export interface Card {
  suit: Suit;
  rank: Rank;
}

export type GamePhase = 'lobby' | 'dealing' | 'bidding' | 'playing' | 'scoring' | 'game_over' | 'finished';
export type ScoringVariant = 'standard' | 'progressive' | 'basic';

export interface PlayerInfo {
  id: string;
  display_name: string;
  seat_index: number;
  is_bot: boolean;
  is_connected: boolean;
  avatar_url?: string;
  card_count: number;
  bid: number | null;
  tricks_won: number;
  score: number;
}

export interface TrickCard {
  player_id: string;
  card: Card;
}

export interface RoundScore {
  player_id: string;
  bid: number;
  tricks_won: number;
  round_points: number;
  cumulative_score: number;
}

export interface GameConfig {
  scoring_variant: ScoringVariant;
  hook_rule: boolean;
  turn_timer_seconds: number;
  max_players: number;
  max_hand_size: number | null;
}

export interface GameState {
  room_code: string;
  phase: GamePhase;
  players: PlayerInfo[];
  host_id: string;
  my_id: string;
  hand: Card[];
  trump_card: Card | null;
  trump_suit: Suit | null;
  current_trick: TrickCard[];
  current_player_id: string | null;
  dealer_id: string | null;
  round_number: number;
  hand_size: number;
  total_rounds: number;
  valid_cards: Card[];
  valid_bids: number[];
  scores_history: RoundScore[][];
  config: GameConfig;
}
