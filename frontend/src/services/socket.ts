import { io, type Socket } from 'socket.io-client';

let socket: Socket | null = null;
let lobbySocket: Socket | null = null;

export function getSocket(): Socket {
  if (!socket) {
    const token = localStorage.getItem('token');
    socket = io('/', {
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
    });
  }
  return socket;
}

export function getLobbySocket(): Socket {
  if (!lobbySocket) {
    lobbySocket = io('/lobby', {
      transports: ['websocket', 'polling'],
      reconnection: true,
    });
  }
  return lobbySocket;
}

export function disconnectSocket() {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
}

export function disconnectLobbySocket() {
  if (lobbySocket) {
    lobbySocket.disconnect();
    lobbySocket = null;
  }
}

export function reconnectSocket() {
  disconnectSocket();
  return getSocket();
}
