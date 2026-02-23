import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import type { PlayerInfo, RoundScore } from '@/types/game';

interface GameOverScreenProps {
  players: PlayerInfo[];
  gameOverData: { final_scores: RoundScore[]; winner_id: string };
}

export default function GameOverScreen({ players, gameOverData }: GameOverScreenProps) {
  const sortedPlayers = [...players].sort((a, b) => b.score - a.score);
  const winner = players.find(p => p.id === gameOverData.winner_id);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-8">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md rounded-xl bg-card border border-border p-8 shadow-2xl text-center"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3, type: 'spring' }}
          className="text-5xl mb-4"
        >
          🏆
        </motion.div>

        <h2 className="text-3xl font-bold mb-1">Game Over!</h2>
        {winner && (
          <p className="text-xl text-accent font-semibold mb-6">
            {winner.display_name} wins with {winner.score} points!
          </p>
        )}

        <div className="space-y-2 mb-6">
          {sortedPlayers.map((player, i) => (
            <motion.div
              key={player.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.1 }}
              className={cn(
                'flex items-center justify-between rounded-lg px-4 py-2',
                i === 0 ? 'bg-accent/10 text-accent' : 'bg-muted',
              )}
            >
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold w-8">{i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`}</span>
                <span className="text-lg font-medium">{player.display_name}</span>
                {player.is_bot && <span className="text-sm">🤖</span>}
              </div>
              <span className="text-lg font-bold">{player.score}</span>
            </motion.div>
          ))}
        </div>

        <div className="flex gap-3 justify-center">
          <Link
            to="/lobby"
            className="rounded-lg bg-primary px-6 py-3 text-lg font-semibold text-primary-foreground hover:opacity-90 transition"
          >
            Play Again
          </Link>
          <Link
            to="/"
            className="rounded-lg bg-secondary px-6 py-3 text-lg font-semibold text-secondary-foreground hover:opacity-90 transition"
          >
            Home
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
