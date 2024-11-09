from typing import List, Optional

from pydantic import BaseModel, field_validator


class GameID(BaseModel):
    gameID: int


class BoardPiece(BaseModel):
    posX: int
    posY: int
    color: str
    isPartial: bool


class BoardPiecePosition(BaseModel):
    posX: int
    posY: int


class FigureCard(BaseModel):
    type: str
    cardID: int
    isBlocked: bool
    gameID: int
    playerID: int


class figureCardID(BaseModel):
    cardID: int


class MovementCard(BaseModel):
    type: str
    cardID: int
    isUsed: bool


class Position(BaseModel):
    posX: int
    posY: int


class MovementCardRequest(BaseModel):
    cardID: int
    playerID: int
    origin: Position
    destination: Position


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
            raise ValueError("La baraja de figuras debe tener un máximo de 3 cartas.")
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
            raise ValueError("El tablero debe tener 36 piezas.")
        return value


class GamePublicInfo(Game):
    figuresToUse: List[List[BoardPiecePosition]]
    timer: float


class Winner(BaseModel):
    winnerID: int
    username: str


class FigureCardRequest(BaseModel):
    cardID: int
    playerID: int
    figure: List[BoardPiecePosition]


class BlockCardRequest(BaseModel):
    cardID: int
    playerID: int
    targetID: int
    figure: List[BoardPiecePosition]
