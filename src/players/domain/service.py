from src.players.domain.model import Player

class PlayerDomaineService:
    def validate_length_name(name: str):
        if len(name) < 1 or len(name) > 32:
            raise ValueError("El nombre debe tener entre 1 y 32 caracteres")
    
    def validate_is_ascii(name: str):
        if not name.isascii():
            raise ValueError("El nombre solo puede contener caracteres ASCII")