from fastapi import HTTPException
from src.players.domain.repository import PlayerRepository

class RepositoryValidators:
    def __init__(self, player_repository: PlayerRepository):
        self.player_repository = player_repository

    def validate_player_exists(self, playerID: int):
        if not self.player_repository.get(playerID):
            raise HTTPException(status_code=404, detail="El jugador proporcionado no existe.")
