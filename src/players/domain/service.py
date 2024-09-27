from src.players.domain.models import PlayerResponse
from fastapi import HTTPException


class DomainService:
    def is_valid_size(username: str):
        if len(username) < 1 or len(username) > 32:
            raise HTTPException(
                status_code=400, detail="El nombre debe tener entre 1 y 32 caracteres")

    def is_ascii(username: str):
        if not username.isascii():
            raise HTTPException(
                status_code=400, detail="El nombre debe ser ASCII")
