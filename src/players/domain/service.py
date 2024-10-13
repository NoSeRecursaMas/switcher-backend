from typing import Optional

from fastapi import HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.players.domain.repository import PlayerRepository


class RepositoryValidators:
    def __init__(self, player_repository: PlayerRepository):
        self.player_repository = player_repository

    async def validate_player_exists(self, playerID: int, websocket: Optional[WebSocket] = None):
        if self.player_repository.get(playerID):
            return
        if websocket is None:
            raise HTTPException(status_code=404, detail="El jugador no existe.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4004, "El jugador no existe.")
