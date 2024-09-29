from pydantic import BaseModel, field_validator
from src.players.domain.service import validate_username


class Player(BaseModel):
    playerID: int
    username: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, value):
        return validate_username(value)


class PlayerCreationRequest(BaseModel):
    username: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, value):
        return validate_username(value)


class PlayerID(BaseModel):
    playerID: int
