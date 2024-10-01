from fastapi import HTTPException
from src.players.domain.repository import PlayerRepository
from src.rooms.domain.repository import RoomRepository


class RepositoryValidators:
    def __init__(self, player_repository: PlayerRepository, room_repository: RoomRepository):
        self.player_repository = player_repository
        self.room_repository = room_repository

    def validate_room_exists(self, roomID: int):
        if not self.room_repository.get(roomID):
            raise HTTPException(
                status_code=404, detail="La sala proporcionada no existe.")

    def validate_player_exists(self, player: int):
        if not self.player_repository.get(player):
            raise HTTPException(
                status_code=404, detail="El jugador proporcionado no existe.")

    def validate_player_is_not_owner(self, playerID):
        if self.room_repository.is_owner(playerID):
            raise HTTPException(
                status_code=405, detail="El propietario no puede abandonar la sala.")

    def validate_player_in_room(self, playerID, roomID):
        if not self.room_repository.is_player_in_room(playerID, roomID):
            raise HTTPException(
                status_code=405, detail="El jugador no se encuentra en la sala.")
