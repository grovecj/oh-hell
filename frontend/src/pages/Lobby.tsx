import { useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSocket } from '@/hooks/useSocket';
import { useGame } from '@/hooks/useGame';
import { getLobbySocket, disconnectLobbySocket } from '@/services/socket';
import type { Socket } from 'socket.io-client';

interface RoomInfo {
  room_code: string;
  host_name: string;
  player_count: number;
  max_players: number;
  scoring_variant: string;
  status: 'waiting' | 'in_progress';
}

export default function Lobby() {
  const navigate = useNavigate();
  const { connected } = useSocket();
  const { createGame, gameState } = useGame();
  const [rooms, setRooms] = useState<RoomInfo[]>([]);
  const [joinCode, setJoinCode] = useState('');

  // Listen for room updates via lobby namespace
  useEffect(() => {
    const lobbySocket: Socket = getLobbySocket();

    lobbySocket.on('rooms_updated', (data: { rooms: RoomInfo[] }) => {
      setRooms(data.rooms);
    });

    return () => {
      lobbySocket.off('rooms_updated');
      disconnectLobbySocket();
    };
  }, []);

  // Navigate to game when created/joined
  useEffect(() => {
    if (gameState?.room_code) {
      navigate(`/game/${gameState.room_code}`);
    }
  }, [gameState?.room_code, navigate]);

  // Listen for game_created event
  const { socket } = useSocket();
  useEffect(() => {
    if (!socket) return;
    const handleCreated = (data: { room_code: string }) => {
      navigate(`/game/${data.room_code}`);
    };
    socket.on('game_created', handleCreated);
    return () => { socket.off('game_created', handleCreated); };
  }, [socket, navigate]);

  const handleJoinByCode = useCallback(() => {
    const code = joinCode.trim().toUpperCase();
    if (code) {
      navigate(`/game/${code}`);
    }
  }, [joinCode, navigate]);

  const handleCreateGame = useCallback(() => {
    createGame();
  }, [createGame]);

  return (
    <div className="min-h-screen p-8">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-3xl font-bold">Game Lobby</h1>
          <Link to="/" className="text-muted-foreground hover:text-foreground transition">
            Back to Home
          </Link>
        </div>

        {/* Join by code + Create game */}
        <div className="mb-8 flex flex-col sm:flex-row gap-4">
          <div className="flex flex-1 gap-2">
            <input
              type="text"
              placeholder="Enter room code..."
              value={joinCode}
              onChange={e => setJoinCode(e.target.value.toUpperCase())}
              onKeyDown={e => e.key === 'Enter' && handleJoinByCode()}
              maxLength={6}
              className="flex-1 rounded-lg border border-border bg-card px-4 py-3 font-mono text-lg tracking-widest placeholder:text-muted-foreground placeholder:tracking-normal placeholder:font-sans focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <button
              onClick={handleJoinByCode}
              disabled={!joinCode.trim()}
              className="rounded-lg bg-primary px-6 py-3 font-semibold text-primary-foreground hover:opacity-90 transition disabled:opacity-50"
            >
              Join
            </button>
          </div>
          <button
            onClick={handleCreateGame}
            disabled={!connected}
            className="rounded-lg bg-accent px-6 py-3 font-semibold text-accent-foreground hover:opacity-90 transition disabled:opacity-50"
          >
            Create Game
          </button>
        </div>

        {/* Room list */}
        <div>
          <h2 className="mb-4 text-xl font-semibold">Games</h2>
          {rooms.length === 0 ? (
            <div className="rounded-xl border border-border bg-card p-12 text-center">
              <p className="text-lg text-muted-foreground mb-2">No games right now</p>
              <p className="text-sm text-muted-foreground">Create one to get started!</p>
            </div>
          ) : (
            <div className="grid gap-3">
              {rooms.map(room => (
                <div
                  key={room.room_code}
                  className="flex items-center justify-between rounded-xl border border-border bg-card p-4 hover:border-primary/50 transition cursor-pointer"
                  onClick={() => navigate(`/game/${room.room_code}`)}
                >
                  <div>
                    <div className="flex items-center gap-3">
                      <span className="font-mono font-bold tracking-wider">{room.room_code}</span>
                      <span className="text-sm text-muted-foreground">by {room.host_name}</span>
                      {room.status === 'in_progress' && (
                        <span className="rounded-full bg-yellow-500/20 px-2 py-0.5 text-xs font-medium text-yellow-400">In Progress</span>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground capitalize">{room.scoring_variant} scoring</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-muted-foreground">
                      {room.player_count}/{room.max_players} players
                    </span>
                    <span className="rounded-lg bg-primary px-3 py-1 text-sm font-medium text-primary-foreground">
                      {room.status === 'waiting' ? 'Join' : 'Watch'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {!connected && (
          <div className="mt-8 rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
            <p className="text-sm text-destructive">Not connected to server. Reconnecting...</p>
          </div>
        )}
      </div>
    </div>
  );
}
