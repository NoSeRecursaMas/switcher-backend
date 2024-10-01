from fastapi import HTTPException


class RepositoryValidators:
    def __init__(self, player_repository):
        self.player_repository = player_repository

    def validate_player_exists(self, player: int):
        if not self.player_repository.get(player):
            raise HTTPException(status_code=404, detail="El jugador proporcionado no existe.")
