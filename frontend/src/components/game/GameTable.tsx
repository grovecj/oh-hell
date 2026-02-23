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
import RoundSummary from './RoundSummary';

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
    gameState, lastTrick, lastRoundScores, gameOverData,
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

  // Debug: log any cards with missing data
  if (hand.some(c => !c.suit || !c.rank)) {
    console.warn('Hand contains invalid cards:', JSON.stringify(hand));
  }

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
    <div className="relative h-screen w-screen overflow-hidden">
      {/* Background image — mansion game room */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: "url('/bg-gameroom.jpg')" }}
      />
      <div className="absolute inset-0 bg-black/50" />

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
        <div
          className="relative w-[90vw] max-w-4xl h-[60vh] rounded-[50%]"
          style={{
            background: 'radial-gradient(ellipse at 40% 40%, #1a6b3c, #145a30 40%, #0f4824 70%, #0a3518)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.5), inset 0 2px 8px rgba(0,0,0,0.3), inset 0 0 60px rgba(0,0,0,0.15)',
          }}
        >
          {/* Felt texture overlay */}
          <div className="absolute inset-0 rounded-[50%] opacity-20" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='4' height='4' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='1' height='1' fill='%23000' fill-opacity='0.15'/%3E%3C/svg%3E")`,
          }} />

          {/* Player seats */}
          {orderedPlayers.map((player, i) => (
            <PlayerSeat
              key={player.id}
              player={player}
              isCurrentPlayer={player.id === current_player_id}
              isDealer={player.id === dealer_id}
              isMe={player.id === my_id}
              position={positions[i] || { x: '50%', y: '50%' }}
              seatIndex={i}
              playerCount={players.length}
            />
          ))}

          {/* Trick area (center of table) */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
            <TrickArea
              currentTrick={current_trick}
              lastTrick={lastTrick}
              orderedPlayerIds={orderedPlayers.map(p => p.id)}
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

      {/* Round summary */}
      {lastRoundScores && (
        <RoundSummary
          scores={lastRoundScores.scores}
          roundNumber={lastRoundScores.round_number}
          players={players}
        />
      )}

      {/* Chat */}
      <Chat />
    </div>
  );
}
