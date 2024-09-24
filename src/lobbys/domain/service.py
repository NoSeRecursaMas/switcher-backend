from fastapi import HTTPException
from src.shared.validators import CommonValidators
from src.players.domain.repository import PlayerRepository


@staticmethod
def validate_min_players_count(min_players: int):
    if min_players < 2:
        raise HTTPException(
            status_code=400, detail="El mínimo de jugadores permitidos es 2.")


@staticmethod
def validate_max_players_count(max_players: int):
    if max_players > 4:
        raise HTTPException(
            status_code=400, detail="El máximo de jugadores permitidos es 4.")


@staticmethod
def validate_min_less_than_max_players(min_players: int, max_players: int):
    if min_players > max_players:
        raise HTTPException(
            status_code=400, detail="El mínimo de jugadores no puede ser mayor al máximo de jugadores.")


class DomaineService:
    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    def validate_lobby_name(lobby_name: str):
        print(lobby_name)
        CommonValidators.is_valid_size(lobby_name)
        CommonValidators.is_ascii(lobby_name)
        CommonValidators.verify_whitespaces(lobby_name)
        CommonValidators.verify_whitespace_count(lobby_name)

    def validate_player_count(min_players: int, max_players: int):
        validate_min_players_count(min_players)
        validate_max_players_count(max_players)
        validate_min_less_than_max_players(min_players, max_players)

    def validate_owner_exists(self, owner: str):
        if not self.repository.find(owner):
            raise HTTPException(
                status_code=404, detail="El propietario proporcionado no existe.")
