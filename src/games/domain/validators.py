from fastapi import HTTPException


class BasicValidators:
    @staticmethod
    def validate_minPlayers(minPlayers: int):
        if minPlayers < 2:
            raise HTTPException(status_code=400, detail="El mínimo de jugadores permitidos es 2.")
