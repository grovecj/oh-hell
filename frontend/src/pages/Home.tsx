import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '@/hooks/useAuth';

const CARD_SUITS = ['♠', '♥', '♦', '♣'];

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 p-8 relative overflow-hidden">
      {/* Decorative background cards */}
      {CARD_SUITS.map((suit, i) => (
        <motion.div
          key={suit}
          className="absolute text-8xl opacity-5 select-none pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{
            opacity: 0.05,
            x: [0, 10, -10, 0],
            y: [0, -10, 10, 0],
          }}
          transition={{ duration: 8, repeat: Infinity, delay: i * 2 }}
          style={{
            top: `${20 + i * 15}%`,
            left: `${10 + i * 20}%`,
          }}
        >
          {suit}
        </motion.div>
      ))}

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center relative z-10"
      >
        <h1 className="mb-2 text-7xl font-extrabold tracking-tight bg-gradient-to-r from-primary via-accent to-trump bg-clip-text text-transparent">
          Oh Hell
        </h1>
        <p className="text-lg text-muted-foreground">
          The classic trick-taking card game, online
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="flex flex-col gap-4 w-full max-w-xs relative z-10"
      >
        <Link
          to="/lobby"
          className="rounded-xl bg-primary px-6 py-4 text-center text-lg font-bold text-primary-foreground transition hover:opacity-90 hover:scale-105 shadow-lg shadow-primary/25"
        >
          Play Now
        </Link>
        <Link
          to="/rules"
          className="rounded-xl bg-secondary px-6 py-3 text-center text-lg font-semibold text-secondary-foreground transition hover:opacity-90"
        >
          How to Play
        </Link>
        <Link
          to="/leaderboard"
          className="rounded-xl bg-secondary px-6 py-3 text-center text-lg font-semibold text-secondary-foreground transition hover:opacity-90"
        >
          Leaderboard
        </Link>
      </motion.div>

      {/* User info */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="absolute top-4 right-4 flex items-center gap-3"
      >
        {user ? (
          <>
            <span className="text-sm text-muted-foreground">{user.display_name}</span>
            {user.is_anonymous ? (
              <Link
                to="/login"
                className="rounded-lg bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground hover:opacity-90 transition"
              >
                Sign In
              </Link>
            ) : (
              <Link
                to="/profile"
                className="rounded-lg bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground hover:opacity-90 transition"
              >
                Profile
              </Link>
            )}
          </>
        ) : (
          <Link
            to="/login"
            className="rounded-lg bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground hover:opacity-90 transition"
          >
            Sign In
          </Link>
        )}
      </motion.div>
    </div>
  );
}
