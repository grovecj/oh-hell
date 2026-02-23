import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { PlayerInfo } from '@/types/game';

interface PlayerSeatProps {
  player: PlayerInfo;
  isCurrentPlayer: boolean;
  isDealer: boolean;
  isMe: boolean;
  position: { x: string; y: string };
}

export default function PlayerSeat({ player, isCurrentPlayer, isDealer, isMe, position }: PlayerSeatProps) {
  return (
    <motion.div
      className={cn(
        'absolute flex flex-col items-center gap-1 -translate-x-1/2 -translate-y-1/2',
      )}
      style={{ left: position.x, top: position.y }}
      animate={isCurrentPlayer ? { scale: [1, 1.05, 1] } : {}}
      transition={{ repeat: Infinity, duration: 1.5 }}
    >
      {/* Avatar / Name */}
      <div className={cn(
        'flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium',
        isCurrentPlayer ? 'bg-primary text-primary-foreground ring-2 ring-primary/50' : 'bg-card text-card-foreground',
        isMe && 'ring-2 ring-accent',
        !player.is_connected && 'opacity-50',
      )}>
        {player.is_bot && <span className="text-xs">🤖</span>}
        <span className="max-w-[80px] truncate">{player.display_name}</span>
        {isDealer && <span className="text-xs font-bold text-trump" title="Dealer">D</span>}
      </div>

      {/* Bid and tricks info */}
      <div className="flex gap-2 text-xs">
        {player.bid !== null && (
          <span className={cn(
            'rounded px-1.5 py-0.5',
            player.bid === player.tricks_won ? 'bg-accent/20 text-accent' : 'bg-muted text-muted-foreground',
          )}>
            {player.tricks_won}/{player.bid}
          </span>
        )}
        {player.card_count > 0 && (
          <span className="rounded bg-muted px-1.5 py-0.5 text-muted-foreground">
            {player.card_count} 🃏
          </span>
        )}
      </div>

      {/* Score */}
      <span className="text-xs font-semibold text-muted-foreground">{player.score} pts</span>
    </motion.div>
  );
}
