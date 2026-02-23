import { motion, AnimatePresence } from 'framer-motion';
import Card from './Card';
import type { TrickCard } from '@/types/game';
import { cn } from '@/lib/utils';

interface TrickAreaProps {
  currentTrick: TrickCard[];
  lastTrick: { winner_id: string; trick: TrickCard[] } | null;
}

// Position offsets for cards in the trick area based on relative seat position
const POSITIONS: Record<number, { x: number; y: number }> = {
  0: { x: 0, y: 40 },     // bottom (current player)
  1: { x: -80, y: 0 },    // left
  2: { x: 0, y: -40 },    // top
  3: { x: 80, y: 0 },     // right
  4: { x: -60, y: -30 },  // top-left
  5: { x: 60, y: -30 },   // top-right
  6: { x: -40, y: 20 },   // bottom-left
};

export default function TrickArea({ currentTrick, lastTrick }: TrickAreaProps) {
  const displayTrick = currentTrick.length > 0 ? currentTrick : (lastTrick?.trick || []);

  return (
    <div className="relative flex items-center justify-center h-48 w-64">
      <AnimatePresence mode="popLayout">
        {displayTrick.map((tc, i) => {
          const pos = POSITIONS[i % 7] || { x: 0, y: 0 };
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
              <Card card={tc.card} small disabled />
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
