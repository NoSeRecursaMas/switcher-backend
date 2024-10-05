from typing import List, Optional
from pydantic import BaseModel

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

class PlayerInfo(BaseModel):
    playerID: int
    username: str
    position: int
    isActive: bool
    sizeDeckFigure: int
    MovementCards: List[MovementCard]
    FigureCards: List[FigureCard]

class Game(BaseModel):
    GameID: int
    Board: List[Board]
    LastMovement: Optional[LastMovement]
    ProhibitedColor: Optional[str]
    players: List[PlayerInfo]

class GameCreationRequest(BaseModel):
    roomID: int

class GameID(BaseModel):
    gameID: int
