from sqlalchemy.orm import Session
from src.players.domain.dbModels import Player
from src.players.domain.service import DomaineService
from src.players.domain.repository import PlayerRepository


class PlayerService():
    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    def create_player(self, request_username: str) -> Player:

        DomaineService.is_valid_size(request_username)
        DomaineService.is_ascii(request_username)

        player = Player(username=request_username)

        return self.repository.save(player)
