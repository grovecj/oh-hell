import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { PlayerInfo, RoundScore } from '@/types/game';

interface RoundSummaryProps {
  scores: RoundScore[];
  roundNumber: number;
  players: PlayerInfo[];
}

export default function RoundSummary({ scores, roundNumber, players }: RoundSummaryProps) {
  // Sort by round points descending
  const sorted = [...scores].sort((a, b) => b.round_points - a.round_points);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
    >
      <div className="rounded-xl bg-card border border-border p-6 shadow-2xl max-w-sm w-full mx-4 pointer-events-auto">
        <h3 className="text-xl font-bold text-center mb-4">
          Round {roundNumber} Results
        </h3>

        <div className="space-y-2">
          {sorted.map(score => {
            const player = players.find(p => p.id === score.player_id);
            const madeBid = score.bid === score.tricks_won;
            return (
              <div
                key={score.player_id}
                className={cn(
                  'flex items-center justify-between rounded-lg px-4 py-2',
                  madeBid ? 'bg-accent/15' : 'bg-muted',
                )}
              >
                <div className="flex items-center gap-2">
                  {madeBid ? (
                    <span className="text-accent text-lg" title="Made bid">&#10003;</span>
                  ) : (
                    <span className="text-destructive text-lg" title="Missed bid">&#10007;</span>
                  )}
                  <span className="font-medium">
                    {player?.display_name ?? 'Unknown'}
                  </span>
                </div>

                <div className="flex items-center gap-4 text-sm">
                  <span className="text-muted-foreground">
                    {score.tricks_won}/{score.bid} tricks
                  </span>
                  <span className={cn(
                    'font-bold min-w-[3ch] text-right',
                    score.round_points > 0 ? 'text-accent' : 'text-muted-foreground',
                  )}>
                    +{score.round_points}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        <p className="text-sm text-muted-foreground text-center mt-4">
          Next round starting...
        </p>
      </div>
    </motion.div>
  );
}
