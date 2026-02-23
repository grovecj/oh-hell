from fastapi import APIRouter

from app.sockets.manager import manager

router = APIRouter(tags=["lobby"])


@router.get("/rooms")
async def list_rooms():
    return manager.get_lobby_rooms()
