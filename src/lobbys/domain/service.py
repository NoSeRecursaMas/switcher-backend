from fastapi import HTTPException
from src.shared.validators import CommonValidators
from src.players.domain.repository import PlayerRepository


class DomainService:
    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    @staticmethod
    def validate_min_players(min_players: int):
        if min_players < 2:
            raise HTTPException(
                status_code=400, detail="El mínimo de jugadores permitidos es 2.")

    @staticmethod
    def validate_max_players(max_players: int):
        if max_players > 4:
            raise HTTPException(
                status_code=400, detail="El máximo de jugadores permitidos es 4.")

    @staticmethod
    def validate_player_range(min_players: int, max_players: int):
        if min_players > max_players:
            raise HTTPException(
                status_code=400, detail="El mínimo de jugadores no puede ser mayor al máximo de jugadores.")

    @staticmethod
    def validate_lobby_name(lobby_name: str):
        CommonValidators.is_valid_size(lobby_name)
        CommonValidators.is_ascii(lobby_name)
        CommonValidators.verify_whitespaces(lobby_name)
        CommonValidators.verify_whitespace_count(lobby_name)

    @staticmethod
    def validate_player_count(min_players: int, max_players: int):
        DomainService.validate_min_players(min_players)
        DomainService.validate_max_players(max_players)
        DomainService.validate_player_range(min_players, max_players)

    def validate_owner_exists(self, owner: str):
        if not self.repository.find(owner):
            raise HTTPException(
                status_code=404, detail="El propietario proporcionado no existe.")
