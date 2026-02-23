import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getProfile, getGoogleLoginUrl } from '@/services/api';

interface ProfileData {
  id: string;
  display_name: string;
  email?: string;
  avatar_url?: string;
  is_anonymous: boolean;
  stats: {
    games_played: number;
    games_won: number;
    total_rounds: number;
    exact_bids: number;
    total_bids: number;
    bid_accuracy: number;
    best_score: number;
    current_streak: number;
    best_streak: number;
  } | null;
}

export default function Profile() {
  const [profile, setProfile] = useState<ProfileData | null>(null);

  useEffect(() => {
    getProfile().then(data => {
      if (!data.error) setProfile(data);
    });
  }, []);

  return (
    <div className="min-h-screen p-8">
      <div className="mx-auto max-w-2xl">
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-3xl font-bold">Profile</h1>
          <Link to="/" className="text-muted-foreground hover:text-foreground transition">
            Back to Home
          </Link>
        </div>

        {profile ? (
          <div className="space-y-6">
            {/* User info */}
            <div className="flex items-center gap-4">
              {profile.avatar_url && (
                <img src={profile.avatar_url} alt="" className="h-16 w-16 rounded-full" />
              )}
              <div>
                <h2 className="text-xl font-bold">{profile.display_name}</h2>
                {profile.email && <p className="text-sm text-muted-foreground">{profile.email}</p>}
                {profile.is_anonymous && (
                  <a
                    href={getGoogleLoginUrl()}
                    className="mt-1 inline-block text-sm text-primary hover:underline"
                  >
                    Sign in with Google to save your stats
                  </a>
                )}
              </div>
            </div>

            {/* Stats */}
            {profile.stats && (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                <StatCard label="Games Played" value={profile.stats.games_played} />
                <StatCard label="Games Won" value={profile.stats.games_won} />
                <StatCard
                  label="Win Rate"
                  value={profile.stats.games_played > 0
                    ? `${Math.round(profile.stats.games_won / profile.stats.games_played * 100)}%`
                    : '—'}
                />
                <StatCard label="Bid Accuracy" value={`${profile.stats.bid_accuracy}%`} />
                <StatCard label="Best Score" value={profile.stats.best_score} />
                <StatCard label="Best Streak" value={profile.stats.best_streak} />
              </div>
            )}
          </div>
        ) : (
          <p className="text-muted-foreground">Loading...</p>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}
