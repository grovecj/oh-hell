import { motion, AnimatePresence } from 'framer-motion';
import Card from './Card';
import type { TrickCard } from '@/types/game';
import { cn } from '@/lib/utils';

interface TrickAreaProps {
  currentTrick: TrickCard[];
  lastTrick: { winner_id: string; trick: TrickCard[] } | null;
  orderedPlayerIds: string[];
}

// Position offsets for cards based on seat index (0 = me at bottom, then clockwise)
const SEAT_OFFSETS: Record<number, Record<number, { x: number; y: number }>> = {
  3: {
    0: { x: 0, y: 80 },
    1: { x: -110, y: 0 },
    2: { x: 110, y: 0 },
  },
  4: {
    0: { x: 0, y: 80 },
    1: { x: -110, y: 0 },
    2: { x: 0, y: -80 },
    3: { x: 110, y: 0 },
  },
  5: {
    0: { x: 0, y: 80 },
    1: { x: -110, y: 20 },
    2: { x: -90, y: -50 },
    3: { x: 90, y: -50 },
    4: { x: 110, y: 20 },
  },
  6: {
    0: { x: 0, y: 80 },
    1: { x: -110, y: 20 },
    2: { x: -90, y: -50 },
    3: { x: 0, y: -80 },
    4: { x: 90, y: -50 },
    5: { x: 110, y: 20 },
  },
  7: {
    0: { x: 0, y: 80 },
    1: { x: -110, y: 30 },
    2: { x: -100, y: -30 },
    3: { x: -50, y: -70 },
    4: { x: 50, y: -70 },
    5: { x: 100, y: -30 },
    6: { x: 110, y: 30 },
  },
};

export default function TrickArea({ currentTrick, lastTrick, orderedPlayerIds }: TrickAreaProps) {
  const displayTrick = currentTrick.length > 0 ? currentTrick : (lastTrick?.trick || []);
  const playerCount = orderedPlayerIds.length;
  const offsets = SEAT_OFFSETS[playerCount] || SEAT_OFFSETS[4];

  return (
    <div className="relative flex items-center justify-center h-72 w-96">
      <AnimatePresence mode="popLayout">
        {displayTrick.map((tc, i) => {
          const seatIndex = orderedPlayerIds.indexOf(tc.player_id);
          const pos = offsets[seatIndex] || { x: 0, y: 0 };
          const isWinner = lastTrick && lastTrick.winner_id === tc.player_id && currentTrick.length === 0;

          return (
            <motion.div
              key={`${tc.card.suit}-${tc.card.rank}-${i}`}
              initial={{ opacity: 0, scale: 0.5, x: pos.x * 2, y: pos.y * 2 }}
              animate={{
                opacity: 1,
                scale: isWinner ? 1.1 : 1,
                x: pos.x,
                y: pos.y,
              }}
              exit={{ opacity: 0, scale: 0.5 }}
              transition={{ duration: 0.3 }}
              className={cn(
                'absolute',
                isWinner && 'ring-2 ring-accent rounded-lg',
              )}
            >
              <Card card={tc.card} size="md" />
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
