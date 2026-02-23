import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useGame } from '@/hooks/useGame';
import { useSocket } from '@/hooks/useSocket';
import GameTable from '@/components/game/GameTable';
import GameLobby from '@/components/game/GameLobby';

export default function Game() {
  const { roomCode } = useParams();
  const { socket, connected } = useSocket();
  const { gameState, joinGame } = useGame();

  useEffect(() => {
    if (connected && roomCode && !gameState) {
      joinGame(roomCode);
    }
  }, [connected, roomCode, gameState, joinGame]);

  useEffect(() => {
    if (socket) {
      const handleError = (data: { message: string }) => {
        console.error('Game error:', data.message);
      };
      socket.on('error', handleError);
      return () => { socket.off('error', handleError); };
    }
  }, [socket]);

  if (!connected) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 text-4xl animate-spin">♠</div>
          <p className="text-muted-foreground">Connecting...</p>
        </div>
      </div>
    );
  }

  if (!gameState) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 text-4xl animate-pulse">🃏</div>
          <p className="text-muted-foreground">Joining game {roomCode}...</p>
        </div>
      </div>
    );
  }

  if (gameState.phase === 'lobby') {
    return <GameLobby />;
  }

  return <GameTable />;
}
