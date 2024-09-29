from fastapi import HTTPException
from src.shared.validators import CommonValidators
from src.players.domain.repository import PlayerRepository
from src.lobbys.domain.repository import LobbyRepository


class DomainService:
    def __init__(self, player_repository: PlayerRepository, lobby_repository: LobbyRepository):
        self.player_repository = player_repository
        self.lobby_repository = lobby_repository

    @staticmethod
    def validate_minPlayers(minPlayers: int):
        if minPlayers < 2:
            raise HTTPException(
                status_code=400, detail="El mínimo de jugadores permitidos es 2.")

    @staticmethod
    def validate_maxPlayers(maxPlayers: int):
        if maxPlayers > 4:
            raise HTTPException(
                status_code=400, detail="El máximo de jugadores permitidos es 4.")

    @staticmethod
    def validate_player_range(minPlayers: int, maxPlayers: int):
        if minPlayers > maxPlayers:
            raise HTTPException(
                status_code=400, detail="El mínimo de jugadores no puede ser mayor al máximo de jugadores.")

    @staticmethod
    def validate_lobby_name(lobby_name: str):
        CommonValidators.is_valid_size(lobby_name)
        CommonValidators.is_ascii(lobby_name)
        CommonValidators.verify_whitespaces(lobby_name)
        CommonValidators.verify_whitespace_count(lobby_name)

    @staticmethod
    def validate_player_count(minPlayers: int, maxPlayers: int):
        DomainService.validate_minPlayers(minPlayers)
        DomainService.validate_maxPlayers(maxPlayers)
        DomainService.validate_player_range(minPlayers, maxPlayers)

    def validate_player_exists(self, player: int):
        if not self.player_repository.find(player):
            raise HTTPException(
                status_code=404, detail="El propietario proporcionado no existe.")
    
    def validate_lobby_exists(self, lobby: int):
        if not self.lobby_repository.find(lobby):
            raise HTTPException(
                status_code=404, detail="La sala no existe.")
