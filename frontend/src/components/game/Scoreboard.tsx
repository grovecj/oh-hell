import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { PlayerInfo, RoundScore } from '@/types/game';

interface ScoreboardProps {
  players: PlayerInfo[];
  scoresHistory: RoundScore[][];
}

export default function Scoreboard({ players, scoresHistory }: ScoreboardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="fixed top-4 right-4 z-40">
      <button
        onClick={() => setExpanded(!expanded)}
        className="rounded-lg bg-card border border-border px-4 py-2.5 text-base font-semibold shadow-lg hover:bg-secondary transition"
      >
        📊 Scoreboard
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, x: 20, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 20, scale: 0.95 }}
            className="absolute top-12 right-0 w-80 max-h-[70vh] overflow-auto rounded-xl bg-card border border-border shadow-2xl"
          >
            <div className="p-4">
              <h3 className="text-lg font-bold mb-3">Scores</h3>

              {/* Current standings */}
              <div className="mb-4 space-y-1">
                {[...players]
                  .sort((a, b) => b.score - a.score)
                  .map((p, i) => (
                    <div key={p.id} className="flex justify-between text-base">
                      <span className="flex items-center gap-1">
                        <span className="text-muted-foreground w-5">{i + 1}.</span>
                        {p.display_name}
                        {p.is_bot && <span className="text-sm">🤖</span>}
                      </span>
                      <span className="font-semibold">{p.score}</span>
                    </div>
                  ))}
              </div>

              {/* Round-by-round history */}
              {scoresHistory.length > 0 && (
                <div className="border-t border-border pt-3">
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Round History</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border">
                          <th className="text-left py-1 pr-2">Player</th>
                          {scoresHistory.map((_, i) => (
                            <th key={i} className="text-center px-1 py-1">R{i + 1}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {players.map(player => (
                          <tr key={player.id} className="border-b border-border/50">
                            <td className="py-1 pr-2 truncate max-w-[60px]">{player.display_name}</td>
                            {scoresHistory.map((round, ri) => {
                              const score = round.find(s => s.player_id === player.id);
                              const hit = score && score.bid === score.tricks_won;
                              return (
                                <td key={ri} className={cn(
                                  'text-center px-1 py-1',
                                  hit ? 'text-accent font-medium' : 'text-muted-foreground',
                                )}>
                                  {score ? `${score.round_points}` : '-'}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
