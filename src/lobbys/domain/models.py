from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class LobbyResponse(BaseModel):
    lobbyID: int


class CreteLobbyRequest(BaseModel):
    owner: int
    lobbyName: str
    min_players: int
    max_players: int
    password: Optional[str] = None

class Status(BaseModel):
    currentTurn: int
    turnOrder: List[int]
    lastColor: int
    board: List[List[int]]
    handMovementCards: List[int]
    players: List[Dict[str, Any]]  # Lista de diccionarios para los jugadores

class WebsocketsUpdateResponse(BaseModel):
    msg: str
    status: Status
