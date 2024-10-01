from src.players.domain.models import Player, PlayerCreationRequest
from src.players.domain.repository import PlayerRepository


class PlayerService:
    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    def create_player(self, player_username: PlayerCreationRequest) -> Player:
        new_player = self.repository.create(player_username)

        return new_player
