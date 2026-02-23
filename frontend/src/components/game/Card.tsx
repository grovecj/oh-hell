import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { Card as CardType } from '@/types/game';

const SUIT_SYMBOLS: Record<string, string> = {
  hearts: '♥',
  diamonds: '♦',
  clubs: '♣',
  spades: '♠',
};

const SUIT_COLORS: Record<string, string> = {
  hearts: 'text-red-500',
  diamonds: 'text-red-500',
  clubs: 'text-foreground',
  spades: 'text-foreground',
};

interface CardProps {
  card: CardType;
  onClick?: () => void;
  disabled?: boolean;
  highlighted?: boolean;
  small?: boolean;
  faceDown?: boolean;
}

export default function Card({ card, onClick, disabled, highlighted, small, faceDown }: CardProps) {
  if (faceDown) {
    return (
      <div className={cn(
        'rounded-lg border-2 border-border bg-primary/20',
        'flex items-center justify-center',
        small ? 'h-16 w-11' : 'h-28 w-20',
      )}>
        <div className="text-2xl text-primary/40">🂠</div>
      </div>
    );
  }

  const symbol = SUIT_SYMBOLS[card.suit];
  const colorClass = SUIT_COLORS[card.suit];

  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      whileHover={!disabled ? { y: -12, scale: 1.05 } : undefined}
      whileTap={!disabled ? { scale: 0.95 } : undefined}
      className={cn(
        'relative rounded-lg border-2 bg-white shadow-md transition-shadow',
        small ? 'h-16 w-11 text-xs' : 'h-28 w-20 text-sm',
        highlighted && !disabled
          ? 'border-primary shadow-lg shadow-primary/25 cursor-pointer'
          : 'border-gray-200',
        disabled && !highlighted && 'opacity-40 cursor-not-allowed',
        !disabled && highlighted && 'hover:shadow-xl',
      )}
    >
      <div className={cn('flex flex-col items-start p-1', colorClass)}>
        <span className={cn('font-bold leading-none', small ? 'text-[10px]' : 'text-base')}>
          {card.rank}
        </span>
        <span className={cn('leading-none', small ? 'text-[10px]' : 'text-sm')}>
          {symbol}
        </span>
      </div>
      <div className={cn(
        'absolute inset-0 flex items-center justify-center',
        colorClass,
        small ? 'text-lg' : 'text-3xl',
      )}>
        {symbol}
      </div>
      <div className={cn(
        'absolute bottom-0 right-0 flex flex-col items-end p-1 rotate-180',
        colorClass,
      )}>
        <span className={cn('font-bold leading-none', small ? 'text-[10px]' : 'text-base')}>
          {card.rank}
        </span>
        <span className={cn('leading-none', small ? 'text-[10px]' : 'text-sm')}>
          {symbol}
        </span>
      </div>
    </motion.button>
  );
}
