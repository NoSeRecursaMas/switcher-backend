from enum import Enum
from typing import Dict

from fastapi.websockets import WebSocket, WebSocketDisconnect, WebSocketState 

class MessageType(str, Enum):
    STATUS = "status"


class ConnectionManagerRoomList:
    active_connections = Dict[int, WebSocket]

    def __init__(self):
        self.active_connections = {}

    def clean_up(self):
        """Limpia la lista de conexiones activas"""
        self.active_connections = {}

    async def connect(self, playerID: int, websocket: WebSocket):
        """Acepta la conexión con el cliente y la almacena.
        En caso de que ese jugador ya esté conectado, se cierra la conexión anterior.

        Args:
            playerID (int): ID del jugador
            websocket (WebSocket): Conexión con el cliente
        """
        await websocket.accept()
        if playerID in self.active_connections:
            await self.active_connections[playerID].close(1000, "Conexión abierta en otra pestaña")
        self.active_connections[playerID] = websocket

    async def keep_listening(self, websocket: WebSocket):
        """Mantiene la conexión abierta con el cliente por tiempo indefinido

        Args:
            websocket (WebSocket): Conexión con el cliente
        """
        try:
            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            connections = self.active_connections.copy()
            for playerID, ws in connections.items():
                if ws == websocket:
                    self.disconnect(playerID)

    def disconnect(self, playerID: int):
        """Desconecta al cliente del jugador

        Args:
            playerID (int): ID del jugador
        """
        ws = self.active_connections.pop(playerID)
        if ws.client_state != WebSocketState.DISCONNECTED:
            ws.close()

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
        for connection in self.active_connections.values():
            await connection.send_json(message)


class ConnectionManagerRoom:
    active_connections = Dict[int, Dict[str, WebSocket]]

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
                await self.active_connections[roomID][playerID].close(1000, "Conexión abierta en otra pestaña")
        if roomID not in self.active_connections:
            self.active_connections[roomID] = {}
        self.active_connections[roomID][playerID] = websocket

    async def keep_listening(self, playerID: int, roomID: int, websocket: WebSocket):
        """Mantiene la conexión abierta con el cliente por tiempo indefinido

        Args:
            playerID (int): ID del jugador
            roomID (int): ID de la sala
            websocket (WebSocket): Conexión con el cliente
        """
        try:
            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            self.disconnect(playerID, roomID)

    def disconnect(self, playerID: int, roomID: int):
        """Desconecta al cliente del jugador en la sala

        Args:
            playerID (int): ID del jugador
            roomID (int): ID de la sala
        """
        ws = self.active_connections[roomID].pop(playerID)
        if ws.client_state != WebSocketState.DISCONNECTED:
            ws.close()

    async def send_personal_message(self, type: MessageType, payload: str, websocket: WebSocket):
        """Envía un mensaje personalizado al cliente

        Args:
            type (str): Tipo de mensaje
            payload (str): Cuerpo del mensaje
            websocket (WebSocket): Conexión con el cliente
        """
        message = {"type": type, "payload": payload}
        await websocket.send_json(message)

    async def broadcast(self, type: MessageType, payload: str, roomID: int):
        """Envía un mensaje a todos los clientes conectados a la sala

        Args:
            type (str): Tipo de mensaje
            payload (str): Cuerpo del mensaje
            roomID (int): ID de la sala
        """
        message = {"type": type, "payload": payload}
        for connection in self.active_connections[roomID].values():
            await connection.send_json(message)


ws_manager_room_list = ConnectionManagerRoomList()
ws_manager_room = ConnectionManagerRoom()
