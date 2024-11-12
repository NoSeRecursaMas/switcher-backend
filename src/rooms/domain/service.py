from typing import Optional

import bcrypt
from fastapi import HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.players.domain.repository import PlayerRepository
from src.rooms.domain.repository import RoomRepository


class RepositoryValidators:
    def __init__(
        self,
        room_repository: RoomRepository,
        player_repository: Optional[PlayerRepository] = None,
    ):
        self.room_repository = room_repository
        self.player_repository = player_repository

    async def validate_room_exists(self, roomID: int, websocket: Optional[WebSocket] = None):
        if self.room_repository.get(roomID) is not None:
            return
        if websocket is None:
            raise HTTPException(status_code=404, detail="La sala no existe.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4004, "La sala no existe.")

    async def validate_player_in_room(self, playerID: int, roomID: int, websocket: Optional[WebSocket] = None):
        if self.room_repository.is_player_in_room(playerID, roomID):
            return
        if websocket is None:
            raise HTTPException(status_code=403, detail="El jugador no se encuentra en la sala.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4003, "El jugador no se encuentra en la sala.")

    def validate_player_is_owner(self, playerID: int, roomID: int):
        if not self.room_repository.is_owner(playerID, roomID):
            raise HTTPException(status_code=403, detail="Solo el propietario puede iniciar la partida.")

    def validate_room_full(self, roomID: int):
        room = self.room_repository.get_public_info(roomID)
        if room is None:
            raise HTTPException(status_code=404, detail="La sala no existe.")
        if len(room.players) >= room.maxPlayers:
            raise HTTPException(status_code=403, detail="La sala está llena.")

    def validate_room_password(self, roomID: int, password: Optional[str] = None):
        room = self.room_repository.get(roomID)

        if room is None:
            raise HTTPException(status_code=404, detail="Sala no encontrada.")

        if room.password:
            if not password or not bcrypt.checkpw(password.encode(), room.password.encode()):
                raise HTTPException(status_code=403, detail="Contraseña incorrecta.")
        elif password:
            raise HTTPException(status_code=403, detail="La sala no tiene contraseña.")

    async def validate_game_not_started(self, roomID: int, websocket: Optional[WebSocket] = None):
        if not self.room_repository.is_game_started(roomID):
            return
        if websocket is None:
            raise HTTPException(status_code=403, detail="La partida ya ha comenzado.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4007, "La partida ya ha comenzado.")
