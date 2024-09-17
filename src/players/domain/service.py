from src.players.domain.dbModels import Player


class DomaineService:
    def is_valid_size(username: str):
        if len(username) < 1 or len(username) > 32:
            raise ValueError("El nombre debe tener entre 1 y 32 caracteres")

    def is_ascii(username: str):
        if not username.isascii():
            raise ValueError("El nombre solo puede contener caracteres ASCII")
