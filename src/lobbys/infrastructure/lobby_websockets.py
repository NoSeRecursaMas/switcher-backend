from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_room_connections: dict[int, list[WebSocket]] = {}

    async def connect_to_room(self, room_id: int, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_room_connections:
            self.active_room_connections[room_id] = []
        self.active_room_connections[room_id].append(websocket)

    def disconnect_from_room(self, room_id: int, websocket: WebSocket):
        if room_id in self.active_room_connections:
            self.active_room_connections[room_id].remove(websocket)
            if not self.active_room_connections[room_id]:
                del self.active_room_connections[room_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_room(self, room_id: int, message: str):
        if room_id in self.active_room_connections:
            for connection in self.active_room_connections[room_id]:
                await connection.send_text(message)
