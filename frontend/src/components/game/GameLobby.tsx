import { useGame } from '@/hooks/useGame';
import { cn } from '@/lib/utils';

export default function GameLobby() {
  const { gameState, startGame, addBot, removeBot, updateConfig, leaveGame } = useGame();

  if (!gameState) return null;

  const { players, host_id, my_id, room_code, config } = gameState;
  const isHost = host_id === my_id;

  return (
    <div className="flex min-h-screen items-center justify-center p-8">
      <div className="w-full max-w-lg rounded-xl bg-card border border-border p-8 shadow-2xl">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold">Game Lobby</h2>
          <div className="mt-2 flex items-center justify-center gap-2">
            <span className="text-sm text-muted-foreground">Room Code:</span>
            <span className="rounded bg-muted px-3 py-1 font-mono text-lg font-bold tracking-wider">
              {room_code}
            </span>
          </div>
        </div>

        {/* Players */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-muted-foreground mb-2">
            Players ({players.length}/{config.max_players})
          </h3>
          <div className="space-y-2">
            {players.map(p => (
              <div key={p.id} className="flex items-center justify-between rounded-lg bg-muted px-4 py-2">
                <div className="flex items-center gap-2">
                  {p.is_bot && <span>🤖</span>}
                  <span className="font-medium">{p.display_name}</span>
                  {p.id === host_id && <span className="text-xs text-accent">(Host)</span>}
                </div>
                {isHost && p.is_bot && (
                  <button
                    onClick={() => removeBot(p.id)}
                    className="text-xs text-destructive hover:underline"
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Host controls */}
        {isHost && (
          <div className="mb-6 space-y-4">
            {/* Add bots */}
            {players.length < config.max_players && (
              <div className="flex gap-2">
                <button
                  onClick={() => addBot('basic')}
                  className="flex-1 rounded-lg bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground hover:opacity-90 transition"
                >
                  + Basic Bot
                </button>
                <button
                  onClick={() => addBot('intermediate')}
                  className="flex-1 rounded-lg bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground hover:opacity-90 transition"
                >
                  + Smart Bot
                </button>
              </div>
            )}

            {/* Game config */}
            <div className="space-y-3 rounded-lg border border-border p-4">
              <h4 className="text-sm font-medium">Game Settings</h4>

              <div className="flex items-center justify-between">
                <label className="text-sm text-muted-foreground">Scoring</label>
                <select
                  value={config.scoring_variant}
                  onChange={e => updateConfig({ scoring_variant: e.target.value })}
                  className="rounded bg-muted px-3 py-1 text-sm"
                >
                  <option value="standard">Standard (+10 + bid)</option>
                  <option value="progressive">Progressive (+10 + bid²)</option>
                  <option value="basic">Basic (+1/trick + 10)</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <label className="text-sm text-muted-foreground">Hook Rule</label>
                <button
                  onClick={() => updateConfig({ hook_rule: !config.hook_rule })}
                  className={cn(
                    'rounded-full px-3 py-1 text-xs font-medium transition',
                    config.hook_rule ? 'bg-accent text-accent-foreground' : 'bg-muted text-muted-foreground',
                  )}
                >
                  {config.hook_rule ? 'On' : 'Off'}
                </button>
              </div>

              <div className="flex items-center justify-between">
                <label className="text-sm text-muted-foreground">Turn Timer</label>
                <select
                  value={config.turn_timer_seconds}
                  onChange={e => updateConfig({ turn_timer_seconds: Number(e.target.value) })}
                  className="rounded bg-muted px-3 py-1 text-sm"
                >
                  <option value={15}>15s</option>
                  <option value={30}>30s</option>
                  <option value={60}>60s</option>
                  <option value={120}>120s</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          {isHost && (
            <button
              onClick={startGame}
              disabled={players.length < 3}
              className={cn(
                'flex-1 rounded-lg px-6 py-3 text-lg font-bold transition',
                players.length >= 3
                  ? 'bg-primary text-primary-foreground hover:opacity-90 cursor-pointer'
                  : 'bg-muted text-muted-foreground cursor-not-allowed',
              )}
            >
              Start Game{players.length < 3 ? ` (need ${3 - players.length} more)` : ''}
            </button>
          )}
          <button
            onClick={leaveGame}
            className="rounded-lg bg-destructive/10 px-4 py-3 text-destructive hover:bg-destructive/20 transition"
          >
            Leave
          </button>
        </div>

        {!isHost && (
          <p className="mt-4 text-center text-sm text-muted-foreground">
            Waiting for the host to start the game...
          </p>
        )}
      </div>
    </div>
  );
}
