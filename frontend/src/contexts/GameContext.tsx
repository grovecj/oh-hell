import { createContext, useCallback, useEffect, useReducer, useContext, type ReactNode } from 'react';
import { SocketContext } from './SocketContext';
import type { Card, GameState, PlayerInfo, RoundScore, TrickCard } from '@/types/game';

type GameAction =
  | { type: 'SET_STATE'; payload: GameState }
  | { type: 'PLAYER_JOINED'; payload: PlayerInfo }
  | { type: 'PLAYER_LEFT'; payload: string }
  | { type: 'BID_PLACED'; payload: { player_id: string; bid: number } }
  | { type: 'CARD_PLAYED'; payload: { player_id: string; card: Card } }
  | { type: 'TRICK_WON'; payload: { winner_id: string; trick: TrickCard[] } }
  | { type: 'ROUND_SCORED'; payload: { scores: RoundScore[]; round_number: number } }
  | { type: 'GAME_OVER'; payload: { final_scores: RoundScore[]; winner_id: string } }
  | { type: 'YOUR_TURN'; payload: { valid_cards?: Card[]; valid_bids?: number[]; time_remaining: number } }
  | { type: 'CARDS_DEALT'; payload: { hand: Card[]; trump_card: Card | null; trump_suit: string | null; hand_size: number; round_number: number } }
  | { type: 'CLEAR' };

interface GameContextState {
  gameState: GameState | null;
  lastTrick: { winner_id: string; trick: TrickCard[] } | null;
  lastRoundScores: { scores: RoundScore[]; round_number: number } | null;
  gameOverData: { final_scores: RoundScore[]; winner_id: string } | null;
  timeRemaining: number;
}

const initialState: GameContextState = {
  gameState: null,
  lastTrick: null,
  lastRoundScores: null,
  gameOverData: null,
  timeRemaining: 0,
};

function gameReducer(state: GameContextState, action: GameAction): GameContextState {
  switch (action.type) {
    case 'SET_STATE':
      return { ...state, gameState: action.payload, lastTrick: null };
    case 'PLAYER_JOINED':
      if (!state.gameState) return state;
      return {
        ...state,
        gameState: {
          ...state.gameState,
          players: [...state.gameState.players.filter(p => p.id !== action.payload.id), action.payload],
        },
      };
    case 'PLAYER_LEFT':
      if (!state.gameState) return state;
      return {
        ...state,
        gameState: {
          ...state.gameState,
          players: state.gameState.players.filter(p => p.id !== action.payload),
        },
      };
    case 'BID_PLACED':
      if (!state.gameState) return state;
      return {
        ...state,
        gameState: {
          ...state.gameState,
          players: state.gameState.players.map(p =>
            p.id === action.payload.player_id ? { ...p, bid: action.payload.bid } : p
          ),
        },
      };
    case 'CARD_PLAYED':
      if (!state.gameState) return state;
      return {
        ...state,
        gameState: {
          ...state.gameState,
          current_trick: [
            ...state.gameState.current_trick,
            { player_id: action.payload.player_id, card: action.payload.card },
          ],
          players: state.gameState.players.map(p =>
            p.id === action.payload.player_id ? { ...p, card_count: p.card_count - 1 } : p
          ),
        },
      };
    case 'TRICK_WON':
      if (!state.gameState) return state;
      return {
        ...state,
        lastTrick: action.payload,
        gameState: {
          ...state.gameState,
          current_trick: [],
          players: state.gameState.players.map(p =>
            p.id === action.payload.winner_id ? { ...p, tricks_won: p.tricks_won + 1 } : p
          ),
        },
      };
    case 'ROUND_SCORED':
      return { ...state, lastRoundScores: action.payload };
    case 'GAME_OVER':
      return { ...state, gameOverData: action.payload };
    case 'YOUR_TURN':
      if (!state.gameState) return state;
      return {
        ...state,
        timeRemaining: action.payload.time_remaining,
        gameState: {
          ...state.gameState,
          valid_cards: action.payload.valid_cards || [],
          valid_bids: action.payload.valid_bids || [],
        },
      };
    case 'CARDS_DEALT':
      if (!state.gameState) return state;
      return {
        ...state,
        gameState: {
          ...state.gameState,
          hand: action.payload.hand,
          trump_card: action.payload.trump_card,
          trump_suit: action.payload.trump_suit as GameState['trump_suit'],
          hand_size: action.payload.hand_size,
          round_number: action.payload.round_number,
        },
      };
    case 'CLEAR':
      return initialState;
    default:
      return state;
  }
}

interface GameContextType extends GameContextState {
  joinGame: (roomCode: string) => void;
  leaveGame: () => void;
  createGame: (config?: Record<string, unknown>) => void;
  startGame: () => void;
  placeBid: (bid: number) => void;
  playCard: (card: Card) => void;
  addBot: (difficulty?: string) => void;
  removeBot: (playerId: string) => void;
  updateConfig: (config: Record<string, unknown>) => void;
  sendChat: (message: string) => void;
}

export const GameContext = createContext<GameContextType>({
  ...initialState,
  joinGame: () => {},
  leaveGame: () => {},
  createGame: () => {},
  startGame: () => {},
  placeBid: () => {},
  playCard: () => {},
  addBot: () => {},
  removeBot: () => {},
  updateConfig: () => {},
  sendChat: () => {},
});

export function GameProvider({ children }: { children: ReactNode }) {
  const { socket } = useContext(SocketContext);
  const [state, dispatch] = useReducer(gameReducer, initialState);

  useEffect(() => {
    if (!socket) return;

    socket.on('game_state', (data: GameState) => dispatch({ type: 'SET_STATE', payload: data }));
    socket.on('player_joined', (data: { player: PlayerInfo }) => dispatch({ type: 'PLAYER_JOINED', payload: data.player }));
    socket.on('player_left', (data: { player_id: string }) => dispatch({ type: 'PLAYER_LEFT', payload: data.player_id }));
    socket.on('bid_placed', (data: { player_id: string; bid: number }) => dispatch({ type: 'BID_PLACED', payload: data }));
    socket.on('card_played', (data: { player_id: string; card: Card }) => dispatch({ type: 'CARD_PLAYED', payload: data }));
    socket.on('trick_won', (data: { winner_id: string; trick: TrickCard[] }) => dispatch({ type: 'TRICK_WON', payload: data }));
    socket.on('round_scored', (data: { scores: RoundScore[]; round_number: number }) => dispatch({ type: 'ROUND_SCORED', payload: data }));
    socket.on('game_over', (data: { final_scores: RoundScore[]; winner_id: string }) => dispatch({ type: 'GAME_OVER', payload: data }));
    socket.on('your_turn', (data: { valid_cards?: Card[]; valid_bids?: number[]; time_remaining: number }) => dispatch({ type: 'YOUR_TURN', payload: data }));
    socket.on('cards_dealt', (data: { hand: Card[]; trump_card: Card | null; trump_suit: string | null; hand_size: number; round_number: number }) => dispatch({ type: 'CARDS_DEALT', payload: data }));

    return () => {
      socket.off('game_state');
      socket.off('player_joined');
      socket.off('player_left');
      socket.off('bid_placed');
      socket.off('card_played');
      socket.off('trick_won');
      socket.off('round_scored');
      socket.off('game_over');
      socket.off('your_turn');
      socket.off('cards_dealt');
    };
  }, [socket]);

  const joinGame = useCallback((roomCode: string) => socket?.emit('join_game', { room_code: roomCode }), [socket]);
  const leaveGame = useCallback(() => { socket?.emit('leave_game'); dispatch({ type: 'CLEAR' }); }, [socket]);
  const createGame = useCallback((config?: Record<string, unknown>) => socket?.emit('create_game', { config }), [socket]);
  const startGame = useCallback(() => socket?.emit('start_game'), [socket]);
  const placeBid = useCallback((bid: number) => socket?.emit('place_bid', { bid }), [socket]);
  const playCard = useCallback((card: Card) => socket?.emit('play_card', { card }), [socket]);
  const addBot = useCallback((difficulty = 'basic') => socket?.emit('add_bot', { difficulty }), [socket]);
  const removeBot = useCallback((playerId: string) => socket?.emit('remove_bot', { player_id: playerId }), [socket]);
  const updateConfig = useCallback((config: Record<string, unknown>) => socket?.emit('update_config', { config }), [socket]);
  const sendChat = useCallback((message: string) => socket?.emit('send_chat', { message }), [socket]);

  return (
    <GameContext.Provider value={{
      ...state,
      joinGame, leaveGame, createGame, startGame,
      placeBid, playCard, addBot, removeBot, updateConfig, sendChat,
    }}>
      {children}
    </GameContext.Provider>
  );
}
