from enum import Enum
from typing import Dict, List

from fastapi.websockets import WebSocket, WebSocketDisconnect, WebSocketState


class MessageType(str, Enum):
    STATUS = "status"
    END = "end"
    MSG = "msg"


class ConnectionManagerGame:
    active_connections: Dict[int, Dict[int, WebSocket]]

    def __init__(self):
        self.active_connections = {}

    def clean_up(self):
        """Limpia la lista de conexiones activas"""
        self.active_connections.clear()

    async def connect(self, playerID: int, gameID: int, websocket: WebSocket):
        """Acepta la conexión con el cliente y la almacena.
        En caso de que ese jugador ya esté conectado a ese juego, se cierra la conexión anterior.

        Args:
            playerID (int): ID del jugador
            gameID (int): ID del juego
            websocket (WebSocket): Conexión con el cliente
        """
        await websocket.accept()
        if gameID in self.active_connections:
            if playerID in self.active_connections[gameID]:
                await self.active_connections[gameID][playerID].close(4005, "Conexión abierta en otra pestaña")
        if gameID not in self.active_connections:
            self.active_connections[gameID] = {}
        self.active_connections[gameID][playerID] = websocket

    async def keep_listening(self, websocket: WebSocket, gameID: int):
        """Mantiene la conexión abierta con el cliente por tiempo indefinido

        Args:
            websocket (WebSocket): Conexión con el cliente
        """
        try:
            while True:
                data = await websocket.receive_json()
                if data["type"] == "msg":
                    await self.broadcast(MessageType.MSG, data["payload"], gameID)

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
        for gameID in active_connections:
            if websocket in active_connections[gameID].values():
                playerID = list(active_connections[gameID].keys())[
                    list(active_connections[gameID].values()).index(websocket)
                ]
                self.active_connections[gameID].pop(playerID)
                if not self.active_connections[gameID]:
                    self.active_connections.pop(gameID)

    async def disconnect_by_id(self, playerID: int, gameID: int):
        """Remueve al cliente de la lista de conexiones activas y cierra la conexión en caso de que no esté cerrada

        Args:
            playerID (int): ID del jugador
            gameID (int): ID del juego
        """
        if gameID in self.active_connections:
            if playerID in self.active_connections[gameID]:
                websocket = self.active_connections[gameID][playerID]
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket.close()
                self.active_connections[gameID].pop(playerID)
                if not self.active_connections[gameID]:
                    self.active_connections.pop(gameID)

    async def send_personal_message(self, type: MessageType, payload: str, websocket: WebSocket):
        """Envía un mensaje personalizado al cliente

        Args:
            type (str): Tipo de mensaje
            payload (str): Cuerpo del mensaje
            websocket (WebSocket): Conexión con el cliente
        """
        message = {"type": type, "payload": payload}
        await websocket.send_json(message)

    async def send_personal_message_by_id(self, type: MessageType, payload: str, playerID: int, gameID: int):
        """Envía un mensaje personalizado al cliente

        Args:
            type (str): Tipo de mensaje
            payload (str): Cuerpo del mensaje
            playerID (int): ID del jugador
            gameID (int): ID del juego
        """
        message = {"type": type, "payload": payload}
        if gameID in self.active_connections:
            if playerID in self.active_connections[gameID]:
                await self.active_connections[gameID][playerID].send_json(message)

    async def broadcast(self, type: MessageType, payload: dict, gameID: int):
        """Envía un mensaje a todos los clientes conectados al juego

        Args:
            type (str): Tipo de mensaje
            payload (dict): Cuerpo del mensaje
            gameID (int): ID del juego
        """
        message = {"type": type, "payload": payload}
        if gameID in self.active_connections:
            for connection in self.active_connections[gameID].values():
                await connection.send_json(message)


ws_manager_game = ConnectionManagerGame()
