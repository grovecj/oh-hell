import type { Card as CardType, GamePhase } from '@/types/game';
import Card from './Card';

interface RoundInfoProps {
  roundNumber: number;
  totalRounds: number;
  handSize: number;
  trumpCard: CardType | null;
  phase: GamePhase;
}

export default function RoundInfo({ roundNumber, totalRounds, handSize, trumpCard, phase }: RoundInfoProps) {
  return (
    <div className="fixed top-4 left-4 z-40 flex items-center gap-3">
      <div className="rounded-lg bg-card border border-border px-3 py-2 shadow-lg text-sm">
        <div className="font-medium">Round {roundNumber}/{totalRounds}</div>
        <div className="text-xs text-muted-foreground">{handSize} card{handSize !== 1 ? 's' : ''}</div>
        <div className="text-xs text-muted-foreground capitalize">{phase}</div>
      </div>

      {trumpCard && (
        <div className="flex flex-col items-center gap-1">
          <span className="text-xs text-muted-foreground">Trump</span>
          <Card card={trumpCard} small disabled />
        </div>
      )}
    </div>
  );
}
