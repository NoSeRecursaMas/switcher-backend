from fastapi import HTTPException


class BasicValidators:
    @staticmethod
    def validate_minPlayers(minPlayers: int):
        if minPlayers < 2:
            raise HTTPException(status_code=400, detail="El mínimo de jugadores permitidos es 2.")

    @staticmethod
    def validate_maxPlayers(maxPlayers: int):
        if maxPlayers > 4:
            raise HTTPException(status_code=400, detail="El máximo de jugadores permitidos es 4.")

    @staticmethod
    def validate_player_range(minPlayers: int, maxPlayers: int):
        if minPlayers > maxPlayers:
            raise HTTPException(
                status_code=400,
                detail="El mínimo de jugadores no puede ser mayor al máximo de jugadores.",
            )

    @classmethod
    def validate_players_count(cls, minPlayers: int, maxPlayers: int):
        cls.validate_minPlayers(minPlayers)
        cls.validate_maxPlayers(maxPlayers)
        cls.validate_player_range(minPlayers, maxPlayers)
