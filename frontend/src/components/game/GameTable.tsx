import { useGame } from '@/hooks/useGame';
import Hand from './Hand';
import TrickArea from './TrickArea';
import BidSelector from './BidSelector';
import PlayerSeat from './PlayerSeat';
import Scoreboard from './Scoreboard';
import GameOverScreen from './GameOverScreen';
import RoundInfo from './RoundInfo';
import Chat from './Chat';
import TurnTimer from './TurnTimer';

// Seat positions around an oval table (percentages)
const SEAT_POSITIONS: Record<number, { x: string; y: string }[]> = {
  3: [
    { x: '50%', y: '90%' },   // me (bottom)
    { x: '15%', y: '40%' },   // left
    { x: '85%', y: '40%' },   // right
  ],
  4: [
    { x: '50%', y: '90%' },   // me (bottom)
    { x: '10%', y: '50%' },   // left
    { x: '50%', y: '10%' },   // top
    { x: '90%', y: '50%' },   // right
  ],
  5: [
    { x: '50%', y: '90%' },
    { x: '10%', y: '60%' },
    { x: '20%', y: '15%' },
    { x: '80%', y: '15%' },
    { x: '90%', y: '60%' },
  ],
  6: [
    { x: '50%', y: '90%' },
    { x: '10%', y: '60%' },
    { x: '15%', y: '20%' },
    { x: '50%', y: '8%' },
    { x: '85%', y: '20%' },
    { x: '90%', y: '60%' },
  ],
  7: [
    { x: '50%', y: '90%' },
    { x: '8%', y: '65%' },
    { x: '10%', y: '25%' },
    { x: '35%', y: '8%' },
    { x: '65%', y: '8%' },
    { x: '90%', y: '25%' },
    { x: '92%', y: '65%' },
  ],
};

export default function GameTable() {
  const {
    gameState, lastTrick, gameOverData,
    placeBid, playCard,
  } = useGame();

  if (!gameState) return null;

  const {
    players, hand, valid_cards, valid_bids, current_trick,
    current_player_id, dealer_id, my_id, phase,
    trump_card, round_number, hand_size, total_rounds,
    scores_history,
  } = gameState;

  const isMyTurn = current_player_id === my_id;
  const showBidSelector = phase === 'bidding' && isMyTurn && valid_bids.length > 0;

  // Reorder players so current player is at bottom (index 0)
  const myIndex = players.findIndex(p => p.id === my_id);
  const orderedPlayers = [
    ...players.slice(myIndex),
    ...players.slice(0, myIndex),
  ];

  const positions = SEAT_POSITIONS[players.length] || SEAT_POSITIONS[4];

  if (gameOverData) {
    return <GameOverScreen players={players} gameOverData={gameOverData} />;
  }

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-background">
      {/* Round info */}
      <RoundInfo
        roundNumber={round_number}
        totalRounds={total_rounds}
        handSize={hand_size}
        trumpCard={trump_card}
        phase={phase}
      />

      {/* Scoreboard */}
      <Scoreboard players={players} scoresHistory={scores_history} />

      {/* Table surface */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative w-[90vw] max-w-4xl h-[60vh] rounded-[50%] bg-gradient-to-b from-emerald-900/30 to-emerald-950/40 border-4 border-emerald-800/30">
          {/* Player seats */}
          {orderedPlayers.map((player, i) => (
            <PlayerSeat
              key={player.id}
              player={player}
              isCurrentPlayer={player.id === current_player_id}
              isDealer={player.id === dealer_id}
              isMe={player.id === my_id}
              position={positions[i] || { x: '50%', y: '50%' }}
            />
          ))}

          {/* Trick area (center of table) */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
            <TrickArea
              currentTrick={current_trick}
              lastTrick={lastTrick}
            />
          </div>
        </div>
      </div>

      {/* Player's hand (bottom) */}
      <div className="absolute bottom-0 left-0 right-0">
        <Hand
          cards={hand}
          validCards={valid_cards}
          onPlayCard={playCard}
          isMyTurn={isMyTurn}
          phase={phase}
        />
      </div>

      {/* Bid selector overlay */}
      {showBidSelector && (
        <BidSelector
          validBids={valid_bids}
          handSize={hand_size}
          onBid={placeBid}
        />
      )}

      {/* Turn timer */}
      <TurnTimer timeRemaining={30} isMyTurn={isMyTurn} />

      {/* Chat */}
      <Chat />
    </div>
  );
}
