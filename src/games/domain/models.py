from typing import List, Optional

from pydantic import BaseModel, field_validator


class GameID(BaseModel):
    gameID: int


class BoardPiece(BaseModel):
    posX: int
    posY: int
    color: str
    isPartial: bool


class FigureCard(BaseModel):
    type: str
    cardID: int
    isBlocked: bool


class MovementCard(BaseModel):
    type: str
    cardID: int
    isUsed: bool

class Position(BaseModel):
    posX: int
    posY: int

class MovementCardRequest(BaseModel):
    card_movementID: int
    playerID: int
    origin: List[Position]
    destination: List[Position]

class PlayerPublicInfo(BaseModel):
    playerID: int
    username: str
    position: int
    isActive: bool
    sizeDeckFigure: int
    cardsFigure: List[FigureCard]

    @field_validator("cardsFigure")
    @classmethod
    def check_size_deck(cls, value):
        if len(value) > 3:
            raise ValueError("The deck of figure cards must have a maximum of 3 cards")
        return value


class Game(BaseModel):
    gameID: int
    board: List[BoardPiece]
    prohibitedColor: Optional[str] = None
    posEnabledToPlay: int
    players: List[PlayerPublicInfo]

    @field_validator("board")
    @classmethod
    def check_board(cls, value):
        if len(value) != 36:
            raise ValueError("The board must have 36 pieces")
        return value


class GamePublicInfo(Game):
    figuresToUse: List[List[BoardPiece]]
    cardsMovement: List[MovementCard]

    @field_validator("cardsMovement")
    @classmethod
    def check_movement_cards(cls, value):
        if len(value) > 3:
            raise ValueError("The deck of movement cards must have a maximum of 3 cards")
        return value
