from typing import Optional

from fastapi import HTTPException

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

    def validate_room_exists(self, roomID: int):
        if not self.room_repository.get(roomID):
            raise HTTPException(status_code=404, detail="La sala proporcionada no existe.")

    def validate_player_is_not_owner(self, playerID: int):
        if self.room_repository.is_owner(playerID):
            raise HTTPException(status_code=404, detail="El propietario no puede abandonar la sala.")

    def validate_player_in_room(self, playerID: int, roomID: int):
        if not self.room_repository.is_player_in_room(playerID, roomID):
            raise HTTPException(status_code=404, detail="El jugador no se encuentra en la sala.")

    def validate_room_full(self, roomID: int):
        room = self.room_repository.get_public_info(roomID)
        if len(room.players) >= room.maxPlayers:
            raise HTTPException(status_code=404, detail="La sala está llena.")
