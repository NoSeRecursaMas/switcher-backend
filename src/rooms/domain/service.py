from fastapi import HTTPException
from src.players.domain.repository import PlayerRepository
from src.rooms.domain.repository import RoomRepository


class RepositoryValidators:
    def __init__(self, player_repository: PlayerRepository, room_repository: RoomRepository):
        self.player_repository = player_repository
        self.room_repository = room_repository

    def validate_room_exists(self, room_id: int):
        if not self.room_repository.get(room_id):
            raise HTTPException(
                status_code=404, detail="La sala proporcionada no existe.")

    def validate_player_exists(self, player: int):
        if not self.player_repository.get(player):
            raise HTTPException(
                status_code=404, detail="El jugador proporcionado no existe.")

    def validate_player_is_not_owner(self, player_id):
        if self.room_repository.is_owner(player_id):
            raise HTTPException(
                status_code=405, detail="El propietario no puede abandonar la sala.")

    def validate_player_in_room(self, player_id, room_id):
        if not self.room_repository.is_player_in_room(player_id, room_id):
            raise HTTPException(
                status_code=405, detail="El jugador no se encuentra en la sala.")
