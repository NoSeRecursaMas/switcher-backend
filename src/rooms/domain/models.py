from typing import List, Optional

from pydantic import BaseModel, ValidationInfo, field_validator, model_validator

from src.players.domain.models import Player
from src.rooms.domain.validators import BasicValidators
from src.shared.validators import CommonValidators


class Room(BaseModel):
    roomID: int
    roomName: str
    minPlayers: int
    maxPlayers: int
    hostID: int
    password: Optional[str] = None
    players: List[Player]


class RoomPublicInfo(BaseModel):
    roomID: int
    roomName: str
    minPlayers: int
    maxPlayers: int
    hostID: int
    players: List[Player]


class RoomExtendedInfo(BaseModel):
    roomID: int
    roomName: str
    maxPlayers: int
    actualPlayers: int
    started: bool
    private: bool
    playersID: List[int]


class RoomID(BaseModel):
    roomID: int


class JoinRoomRequest(BaseModel):
    playerID: int
    password: Optional[str] = None


class RoomCreationRequest(BaseModel):
    playerID: int
    roomName: str
    minPlayers: int
    maxPlayers: int
    password: Optional[str] = None

    @field_validator("roomName")
    @classmethod
    def validate_roomName(cls, value: str, info: ValidationInfo):
        return CommonValidators.validate_string(value, info)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: Optional[str], info: ValidationInfo):
        return CommonValidators.validate_password(value, info)

    @model_validator(mode="before")
    @classmethod
    def validate_players_count(cls, values):
        minPlayers = values.get("minPlayers")
        maxPlayers = values.get("maxPlayers")
        BasicValidators.validate_players_count(minPlayers, maxPlayers)
        return values
