import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { PlayerInfo } from '@/types/game';
import Card from './Card';

interface PlayerSeatProps {
  player: PlayerInfo;
  isCurrentPlayer: boolean;
  isDealer: boolean;
  isMe: boolean;
  position: { x: string; y: string };
  seatIndex: number;
  playerCount: number;
}

// Rotation angles so each player's hand fans toward the center of the table
const HAND_ROTATION: Record<number, Record<number, number>> = {
  3: { 1: 120, 2: -120 },
  4: { 1: 90, 2: 180, 3: -90 },
  5: { 1: 100, 2: 150, 3: -150, 4: -100 },
  6: { 1: 100, 2: 140, 3: 180, 4: -140, 5: -100 },
  7: { 1: 95, 2: 130, 3: 160, 4: -160, 5: -130, 6: -95 },
};

// Offset the card fan OUTWARD from table center (behind the player info)
// so it looks like the player is holding cards from their seat at the edge.
function getFanOffset(seatIndex: number, playerCount: number): { x: number; y: number } {
  if (seatIndex === 0) return { x: 0, y: 0 };
  const rotation = HAND_ROTATION[playerCount]?.[seatIndex] ?? 0;
  const rad = (rotation * Math.PI) / 180;
  // Offset AWAY from center (negative = outward)
  const dist = -70;
  return { x: Math.sin(rad) * dist, y: -Math.cos(rad) * dist };
}

function FaceDownHand({ count, rotation }: { count: number; rotation: number }) {
  if (count <= 0) return null;
  const cardWidth = 110; // md card width
  const exposed = 28;
  const fanWidth = cardWidth + (count - 1) * exposed;
  return (
    <div
      className="relative flex justify-center"
      style={{
        height: 160, // md card height
        width: fanWidth,
        transform: `rotate(${rotation}deg)`,
      }}
    >
      {Array.from({ length: count }, (_, i) => {
        const center = (count - 1) / 2;
        const offset = i - center;
        const cardRotation = offset * 4;
        return (
          <div
            key={i}
            className="absolute"
            style={{
              transform: `translateX(${offset * exposed}px) rotate(${cardRotation}deg)`,
              transformOrigin: 'bottom center',
              zIndex: i,
            }}
          >
            <Card card={{ suit: 'spades', rank: 'A' }} size="md" faceDown />
          </div>
        );
      })}
    </div>
  );
}

function Avatar({ player }: { player: PlayerInfo }) {
  if (player.avatar_url) {
    return (
      <img
        src={player.avatar_url}
        alt=""
        className="h-12 w-12 rounded-full border-2 border-white/30 object-cover"
      />
    );
  }
  // Fallback: colored circle with first letter
  return (
    <div className="flex h-12 w-12 items-center justify-center rounded-full border-2 border-white/30 bg-muted text-lg font-bold text-muted-foreground">
      {player.display_name.charAt(0).toUpperCase()}
    </div>
  );
}

export default function PlayerSeat({ player, isCurrentPlayer, isDealer, isMe, position, seatIndex, playerCount }: PlayerSeatProps) {
  const fanOffset = getFanOffset(seatIndex, playerCount);
  const rotation = HAND_ROTATION[playerCount]?.[seatIndex] ?? 0;

  return (
    <motion.div
      className={cn(
        'absolute flex flex-col items-center -translate-x-1/2 -translate-y-1/2',
      )}
      style={{ left: position.x, top: position.y }}
      animate={isCurrentPlayer ? { scale: [1, 1.05, 1] } : {}}
      transition={{ repeat: Infinity, duration: 1.5 }}
    >
      {/* Face-down cards for opponents — absolutely positioned with offset */}
      {!isMe && player.card_count > 0 && (
        <div
          className="absolute"
          style={{
            transform: `translate(${fanOffset.x}px, ${fanOffset.y}px)`,
            zIndex: 0,
          }}
        >
          <FaceDownHand count={player.card_count} rotation={rotation} />
        </div>
      )}

      {/* Player info (avatar + name + score) — stays in place */}
      <div className="relative z-10 flex flex-col items-center gap-1">
        <Avatar player={player} />

        <div className={cn(
          'flex items-center gap-2 rounded-full px-4 py-2 text-base font-semibold',
          isCurrentPlayer ? 'bg-primary text-primary-foreground ring-2 ring-primary/50' : 'bg-card text-card-foreground',
          isMe && 'ring-2 ring-accent',
          !player.is_connected && 'opacity-50',
        )}>
          {player.is_bot && <span className="text-sm">🤖</span>}
          <span className="max-w-[100px] truncate">{player.display_name}</span>
          {isDealer && <span className="text-sm font-bold text-trump" title="Dealer">D</span>}
        </div>

        {/* Bid and tricks info */}
        <div className="flex gap-2 text-sm">
          {player.bid !== null && (
            <span className={cn(
              'rounded px-2 py-0.5 font-medium',
              player.bid === player.tricks_won ? 'bg-accent/20 text-accent' : 'bg-muted text-muted-foreground',
            )}>
              {player.tricks_won}/{player.bid}
            </span>
          )}
        </div>

        {/* Score */}
        <span className="text-sm font-bold text-muted-foreground">{player.score} pts</span>
      </div>
    </motion.div>
  );
}
