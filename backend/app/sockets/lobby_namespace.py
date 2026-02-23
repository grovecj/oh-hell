import socketio

from app.sockets.manager import manager


class LobbyNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ, auth=None):
        # Lobby namespace doesn't require auth — anyone can browse rooms
        rooms = manager.get_lobby_rooms()
        await self.emit("rooms_updated", {"rooms": rooms}, to=sid)

    async def on_disconnect(self, sid):
        pass
