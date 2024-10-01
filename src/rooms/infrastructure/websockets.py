from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_room_connections: dict[int, list[WebSocket]] = {}
        self.players_connections: dict[int, WebSocket] = {}

    async def connect_to_room(self, roomID: int, playerID: int, websocket: WebSocket):
        await websocket.accept()
        if roomID not in self.active_room_connections:
            self.active_room_connections[roomID] = []
        if playerID not in self.players_connections:
            self.players_connections[playerID] = websocket
        if websocket not in self.active_room_connections[roomID]:
            self.active_room_connections[roomID].append(websocket)

    async def disconnect_from_room(self, roomID: int, playerID: int, websocket: WebSocket):
        if roomID in self.active_room_connections:
            self.active_room_connections[roomID].remove(websocket)
            if not self.active_room_connections[roomID]:
                del self.active_room_connections[roomID]
            if playerID in self.players_connections:
                del self.players_connections[playerID]
            await websocket.close()

    async def send_personal_message(self, message: dict, playerID: int):
        if playerID in self.players_connections:
            websocket = self.players_connections[playerID]
            await websocket.send_json(message)

    async def broadcast_to_room(self, roomID: int, message: dict):
        if roomID in self.active_room_connections:
            for connection in self.active_room_connections[roomID]:
                await connection.send_json(message)
