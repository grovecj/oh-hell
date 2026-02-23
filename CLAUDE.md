# Oh Hell Online

Real-time multiplayer card game web app.

## Tech Stack
- Backend: Python 3.12 + FastAPI + python-socketio (async ASGI)
- Frontend: React 19 + TypeScript + Vite + Tailwind CSS + shadcn/ui + Framer Motion
- Real-time: Socket.IO (python-socketio server, socket.io-client)
- Database: PostgreSQL 16 (shared DO managed cluster)
- ORM: SQLAlchemy 2.0 (async) + Alembic
- Auth: Google OAuth (authlib) + JWT, anonymous-first
- Infra: Co-hosted on cartergrove-me droplet, Nginx + PM2, Terraform

## Project Structure
- `backend/app/` — FastAPI application
  - `game/` — Pure game engine (zero I/O dependencies)
  - `sockets/` — Socket.IO handlers + room manager
  - `api/` — REST endpoints (auth, lobby, users, health)
  - `models/` — SQLAlchemy ORM models
  - `schemas/` — Pydantic request/response schemas
  - `services/` — Business logic (game, auth, stats)
  - `bot/` — AI bot strategies
- `frontend/src/` — React SPA
  - `components/game/` — Game table, hand, cards, scoreboard
  - `components/lobby/` — Room list, create/join
  - `contexts/` — AuthContext, SocketContext, GameContext
  - `hooks/` — useSocket, useGame, useAuth
  - `pages/` — Route pages
- `terraform/` — Infrastructure as code
- `nginx/` — Reverse proxy config

## Local Development
```sh
docker compose up -d           # Start PostgreSQL
cd backend && uv sync          # Install Python dependencies
cd backend && uv run uvicorn app.main:app --reload  # Start backend
cd frontend && npm install     # Install frontend dependencies
cd frontend && npm run dev     # Start frontend dev server
```

## Commands
- `cd backend && uv run pytest` — Run backend tests
- `cd backend && uv run alembic upgrade head` — Run migrations
- `cd backend && uv run ruff check .` — Lint backend
- `cd frontend && npm run dev` — Start frontend dev server
- `cd frontend && npm run build` — Build frontend
- `cd frontend && npm run lint` — Lint frontend

## Conventions
- Game engine (`backend/app/game/`) has zero I/O dependencies — pure Python logic
- Active games live in memory; only persist results to DB on game_over
- Socket.IO for all real-time game communication
- REST API for auth, lobby listing, stats, health
- Anonymous-first auth: zero friction to start playing
- Use `@/` import alias in frontend for `src/`
- All Pydantic models use `model_config = ConfigDict(from_attributes=True)`
