import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getLeaderboard } from '@/services/api';
import { cn } from '@/lib/utils';

interface LeaderboardEntry {
  display_name: string;
  avatar_url: string | null;
  games_played: number;
  games_won: number;
  win_rate: number;
  bid_accuracy: number;
  best_score: number;
  best_streak: number;
}

export default function Leaderboard() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLeaderboard()
      .then(data => {
        if (Array.isArray(data)) setEntries(data);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen p-8">
      <div className="mx-auto max-w-3xl">
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-3xl font-bold">Leaderboard</h1>
          <Link to="/" className="text-muted-foreground hover:text-foreground transition">
            Back to Home
          </Link>
        </div>

        {loading ? (
          <p className="text-muted-foreground">Loading...</p>
        ) : entries.length === 0 ? (
          <div className="rounded-xl border border-border bg-card p-12 text-center">
            <p className="text-lg text-muted-foreground">No players on the leaderboard yet</p>
            <p className="text-sm text-muted-foreground mt-1">Sign in and play games to appear here!</p>
          </div>
        ) : (
          <div className="rounded-xl border border-border overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted">
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">#</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Player</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">Won</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">Win%</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">Bid%</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">Best</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry, i) => (
                  <tr key={i} className={cn('border-b border-border/50', i < 3 && 'bg-accent/5')}>
                    <td className="px-4 py-3 font-bold">
                      {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : i + 1}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {entry.avatar_url && (
                          <img src={entry.avatar_url} alt="" className="h-6 w-6 rounded-full" />
                        )}
                        <span className="font-medium">{entry.display_name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">{entry.games_won}/{entry.games_played}</td>
                    <td className="px-4 py-3 text-right">{entry.win_rate}%</td>
                    <td className="px-4 py-3 text-right">{entry.bid_accuracy}%</td>
                    <td className="px-4 py-3 text-right font-semibold">{entry.best_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
