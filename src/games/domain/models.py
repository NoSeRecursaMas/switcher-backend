from typing import List, Optional

from pydantic import BaseModel, ValidationInfo, field_validator, model_validator
from pydantic.types import Json


class Board(BaseModel):
    PosX: int
    PosY: int
    Color: str


class LastMovement(BaseModel):
    PosX1: int
    PosY1: int
    PosX2: int
    PosY2: int
    Order: int
    CardID: int


class MovementCard(BaseModel):
    type: str
    cardID: int
    isDiscarded: bool


class FigureCard(BaseModel):
    type: str
    cardID: int
    isBlocked: bool


class PlayerInfoPublic(BaseModel):
    playerID: int
    username: str
    position: int
    isActive: bool
    sizeDeckFigure: int
    FigureCards: List[FigureCard]

class PlayerInfoPrivate(BaseModel):
    playerID: int
    MovementCards: List[MovementCard]

class Game(BaseModel):
    GameID: int
    Board: List[Board]
    posEnabledToPlay: int
    LastMovement: Optional[LastMovement]
    ProhibitedColor: Optional[str]
    players: List[PlayerInfoPublic]


class GameCreationRequest(BaseModel):
    roomID: int
    board: List[Board]


class GameID(BaseModel):
    gameID: int