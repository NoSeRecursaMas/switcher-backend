from sqlalchemy.orm import Session
from src.players.domain.models import PlayerResponse, PlayerUsername
from src.players.domain.service import DomaineService
from src.players.domain.repository import PlayerRepository


class PlayerService():
    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    def create_player(self, request_username: PlayerUsername) -> PlayerResponse:

        DomaineService.is_valid_size(request_username.username)
        DomaineService.is_ascii(request_username.username)

        saved_player = self.repository.save(request_username)

        return saved_player
