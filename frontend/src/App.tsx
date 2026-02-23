import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '@/contexts/AuthContext'
import { SocketProvider } from '@/contexts/SocketContext'
import { GameProvider } from '@/contexts/GameContext'
import Home from '@/pages/Home'
import Lobby from '@/pages/Lobby'
import Game from '@/pages/Game'
import Profile from '@/pages/Profile'
import Leaderboard from '@/pages/Leaderboard'
import Rules from '@/pages/Rules'
import Login from '@/pages/Login'

function App() {
  return (
    <AuthProvider>
      <SocketProvider>
        <GameProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/lobby" element={<Lobby />} />
              <Route path="/game/:roomCode" element={<Game />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/leaderboard" element={<Leaderboard />} />
              <Route path="/rules" element={<Rules />} />
              <Route path="/login" element={<Login />} />
            </Routes>
          </BrowserRouter>
        </GameProvider>
      </SocketProvider>
    </AuthProvider>
  )
}

export default App
