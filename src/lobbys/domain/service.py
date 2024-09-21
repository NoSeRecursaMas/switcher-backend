from fastapi import HTTPException
from src.shared.validators import CommonValidators
from src.players.domain.repository import PlayerRepository


class DomaineService:
    def __init__(self, repository: PlayerRepository):
        self.repository = repository

    def validate_lobby_name(lobby_name: str):
        print(lobby_name)
        CommonValidators.is_valid_size(lobby_name)
        CommonValidators.is_ascii(lobby_name)

    def validate_owner_exist(self, owner: str):
        if not self.repository.find(owner):
            raise HTTPException(status_code=404, detail="Owner not found")
