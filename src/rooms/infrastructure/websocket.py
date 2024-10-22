from enum import Enum
from typing import Dict, List

from fastapi.websockets import WebSocket, WebSocketDisconnect, WebSocketState


class MessageType(str, Enum):
    STATUS = "status"
    START_GAME = "start"
    END_ROOM = "end"


class ConnectionManagerRoomList:
    active_connections: List[WebSocket]

    def __init__(self):
        self.active_connections = []

    def clean_up(self):
        """Limpia la lista de conexiones activas"""
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        """Acepta la conexión con el cliente y la almacena.

        Args:
            websocket (WebSocket): Conexión con el cliente
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    async def keep_listening(self, websocket: WebSocket):
        """Mantiene la conexión abierta con el cliente por tiempo indefinido

        Args:
            websocket (WebSocket): Conexión con el cliente
        """
        try:
            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            await self.disconnect(websocket)

    async def disconnect(self, websocket: WebSocket):
        """Remueve al cliente de la lista de conexiones activas

        Args:
            websocket (WebSocket): Conexión con el cliente
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()

    async def send_personal_message(self, type: MessageType, payload, websocket: WebSocket):
        """Envía un mensaje personalizado al cliente

        Args:
            type (str): Tipo de mensaje
            payload (str): Cuerpo del mensaje
            websocket (WebSocket): Conexión con el cliente
        """
        message = {"type": type, "payload": payload}
        await websocket.send_json(message)

    async def broadcast(self, type: MessageType, payload):
        """Envía un mensaje a todos los clientes conectados

        Args:
            type (str): Tipo de mensaje
            payload (str): Cuerpo del mensaje
        """
        message = {"type": type, "payload": payload}
        for connection in self.active_connections:
            await connection.send_json(message)


class ConnectionManagerRoom:
    active_connections: Dict[int, Dict[int, WebSocket]]

    def __init__(self):
        self.active_connections = {}

    def clean_up(self):
        """Limpia la lista de conexiones activas"""
        self.active_connections.clear()

    async def connect(self, playerID: int, roomID: int, websocket: WebSocket):
        """Acepta la conexión con el cliente y la almacena.
        En caso de que ese jugador ya esté conectado a esa sala, se cierra la conexión anterior.

        Args:
            playerID (int): ID del jugador
            roomID (int): ID de la sala
            websocket (WebSocket): Conexión con el cliente
        """
        await websocket.accept()
        if roomID in self.active_connections:
            if playerID in self.active_connections[roomID]:
                await self.active_connections[roomID][playerID].close(4005, "Conexión abierta en otra pestaña")
        if roomID not in self.active_connections:
            self.active_connections[roomID] = {}
        self.active_connections[roomID][playerID] = websocket

    async def keep_listening(self, websocket: WebSocket):
        """Mantiene la conexión abierta con el cliente por tiempo indefinido

        Args:
            websocket (WebSocket): Conexión con el cliente
        """
        try:
            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            await self.disconnect(websocket)

    async def disconnect(self, websocket: WebSocket):
        """Remueve al cliente de la lista de conexiones activas y cierra la conexión en caso de que no esté cerrada

        Args:
            websocket (WebSocket): Conexión con el cliente
        """
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
        active_connections = self.active_connections.copy()
        for roomID in active_connections:
            if websocket in active_connections[roomID].values():
                playerID = list(active_connections[roomID].keys())[
                    list(active_connections[roomID].values()).index(websocket)
                ]
                self.active_connections[roomID].pop(playerID)
                if not self.active_connections[roomID]:
                    self.active_connections.pop(roomID)

    async def disconnect_by_id_room(self, playerID: int, roomID: int):
        """Remueve al cliente de la lista de conexiones activas y cierra la conexión en caso de que no esté cerrada

        Args:
            playerID (int): ID del jugador
            roomID (int): ID de la sala
        """
        if roomID in self.active_connections:
            if playerID in self.active_connections[roomID]:
                websocket = self.active_connections[roomID][playerID]
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket.close()
                self.active_connections[roomID].pop(playerID)
                if not self.active_connections[roomID]:
                    self.active_connections.pop(roomID)

    async def send_personal_message(self, type: MessageType, payload: str, websocket: WebSocket):
        """Envía un mensaje personalizado al cliente

        Args:
            type (str): Tipo de mensaje
            payload (str): Cuerpo del mensaje
            websocket (WebSocket): Conexión con el cliente
        """
        message = {"type": type, "payload": payload}
        await websocket.send_json(message)

    async def send_personal_message_by_id(self, type: MessageType, payload: str, playerID: int, roomID: int):
        """Envía un mensaje personalizado al cliente

        Args:
            type (str): Tipo de mensaje
            payload (str): Cuerpo del mensaje
            playerID (int): ID del jugador
            roomID (int): ID de la sala
        """
        message = {"type": type, "payload": payload}
        if roomID in self.active_connections:
            if playerID in self.active_connections[roomID]:
                await self.active_connections[roomID][playerID].send_json(message)

    async def broadcast(self, type: MessageType, payload: str, roomID: int):
        """Envía un mensaje a todos los clientes conectados a la sala

        Args:
            type (str): Tipo de mensaje
            payload (str): Cuerpo del mensaje
            roomID (int): ID de la sala
        """
        message = {"type": type, "payload": payload}
        if roomID in self.active_connections:
            for connection in self.active_connections[roomID].values():
                await connection.send_json(message)


ws_manager_room_list = ConnectionManagerRoomList()
ws_manager_room = ConnectionManagerRoom()
