import { createContext, useEffect, useState, type ReactNode } from 'react';
import { type Socket } from 'socket.io-client';
import { getSocket, disconnectSocket } from '@/services/socket';

interface SocketContextType {
  socket: Socket | null;
  connected: boolean;
}

export const SocketContext = createContext<SocketContextType>({
  socket: null,
  connected: false,
});

export function SocketProvider({ children }: { children: ReactNode }) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    const s = getSocket();
    setSocket(s);

    s.on('connect', () => setConnected(true));
    s.on('disconnect', () => setConnected(false));

    return () => {
      disconnectSocket();
      setSocket(null);
      setConnected(false);
    };
  }, []);

  return (
    <SocketContext.Provider value={{ socket, connected }}>
      {children}
    </SocketContext.Provider>
  );
}
