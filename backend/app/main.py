import logging
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logging.getLogger("app").setLevel(logging.DEBUG)

from app.config import settings
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.lobby import router as lobby_router
from app.api.users import router as users_router
from app.sockets.handlers import register_handlers
from app.sockets.lobby_namespace import LobbyNamespace

app = FastAPI(title="Oh Hell Online", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API routes
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(lobby_router, prefix="/api/lobby")
app.include_router(users_router, prefix="/api/users")

# Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[settings.frontend_url, "http://localhost:5173"],
    logger=False,
    engineio_logger=False,
)

register_handlers(sio)
sio.register_namespace(LobbyNamespace("/lobby"))

# Mount Socket.IO as ASGI sub-app
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Serve static frontend files in production
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

# The final ASGI app (uvicorn points at this)
app = socket_app
