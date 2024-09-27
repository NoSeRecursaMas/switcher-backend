from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_room_connections: dict[int, list[WebSocket]] = {}
        self.players_connections: dict[int, WebSocket] = {}

    async def connect_to_room(self, room_id: int, player_id: int, websocket: WebSocket):
        try:
            await websocket.accept()
            if room_id not in self.active_room_connections:
                self.active_room_connections[room_id] = []
            if player_id not in self.players_connections:
                self.players_connections[player_id] = websocket
            if websocket not in self.active_room_connections[room_id]:
                self.active_room_connections[room_id].append(websocket)
        except Exception as e:
            raise RuntimeError(f"Error connecting to room {
                               room_id} for player {player_id}")

    async def disconnect_from_room(self, room_id: int, player_id: int, websocket: WebSocket):
        try:
            if room_id in self.active_room_connections:
                self.active_room_connections[room_id].remove(websocket)
                if not self.active_room_connections[room_id]:
                    del self.active_room_connections[room_id]
                if player_id in self.players_connections:
                    del self.players_connections[player_id]
                await websocket.close()
        except Exception as e:
            raise RuntimeError(f"Error disconnecting from room {
                               room_id} for player {player_id}")

    async def send_personal_message(self, message: dict, player_id: int):
        try:
            if player_id in self.players_connections:
                websocket = self.players_connections[player_id]
                await websocket.send_json(message)
        except Exception as e:
            raise RuntimeError(
                f"Error sending personal message to player {player_id}")

    async def broadcast_to_room(self, room_id: int, message: dict):
        try:
            if room_id in self.active_room_connections:
                for connection in self.active_room_connections[room_id]:
                    await connection.send_json(message)
        except Exception as e:
            raise RuntimeError(f"Error broadcasting to room {room_id}")
