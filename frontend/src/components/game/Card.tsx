import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { Card as CardType } from '@/types/game';

const SUIT_ABBREV: Record<string, string> = {
  hearts: 'H',
  diamonds: 'D',
  clubs: 'C',
  spades: 'S',
};

function getCardImageUrl(card: CardType): string {
  const suit = SUIT_ABBREV[card.suit] || 'S';
  return `/cards/${card.rank}${suit}.svg`;
}

type CardSize = 'sm' | 'md' | 'lg';

const SIZE_CLASSES: Record<CardSize, string> = {
  sm: 'h-24 w-[66px]',
  md: 'h-40 w-[110px]',
  lg: 'h-[216px] w-[156px]',
};

interface CardProps {
  card: CardType;
  onClick?: () => void;
  disabled?: boolean;
  highlighted?: boolean;
  size?: CardSize;
  faceDown?: boolean;
}

export default function Card({ card, onClick, disabled, highlighted, size = 'lg', faceDown }: CardProps) {
  if (faceDown) {
    return (
      <div className={cn(
        'rounded-lg overflow-hidden shadow-md',
        SIZE_CLASSES[size],
      )}>
        <img src="/cards/back.svg" alt="Card back" className="h-full w-full object-cover" />
      </div>
    );
  }

  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      whileHover={!disabled ? { y: -16, scale: 1.08 } : undefined}
      whileTap={!disabled ? { scale: 0.95 } : undefined}
      className={cn(
        'relative rounded-lg overflow-hidden shadow-md transition-shadow',
        SIZE_CLASSES[size],
        highlighted && !disabled
          ? 'ring-2 ring-primary ring-offset-2 ring-offset-background shadow-lg shadow-primary/30 cursor-pointer'
          : '',
        disabled && !highlighted && 'cursor-not-allowed',
        !disabled && highlighted && 'hover:shadow-xl',
      )}
    >
      <img
        src={getCardImageUrl(card)}
        alt={`${card.rank} of ${card.suit}`}
        className="h-full w-full object-contain"
        draggable={false}
      />
    </motion.button>
  );
}
