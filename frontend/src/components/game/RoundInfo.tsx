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
    <div className="fixed top-4 left-4 z-40 flex items-center gap-4">
      <div className="rounded-lg bg-card border border-border px-4 py-3 shadow-lg">
        <div className="text-lg font-bold">Round {roundNumber}/{totalRounds}</div>
        <div className="text-sm text-muted-foreground">{handSize} card{handSize !== 1 ? 's' : ''}</div>
        <div className="text-sm text-muted-foreground capitalize">{phase}</div>
      </div>

      {trumpCard && (
        <div className="flex flex-col items-center gap-1">
          <span className="text-sm font-medium text-muted-foreground">Trump</span>
          <Card card={trumpCard} size="md" disabled />
        </div>
      )}
    </div>
  );
}
