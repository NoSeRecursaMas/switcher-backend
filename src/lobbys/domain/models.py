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

class RoomInfo(BaseModel):
    hostID: int
    roomID: int
    roomName: str
    minPlayers: int
    maxPlayers: int
    players: List[Dict[str, Any]] 

class Status(BaseModel):
    currentTurn: int
    turnOrder: List[int]
    lastColor: int
    board: List[List[int]]
    handMovementCards: List[int]
    players: List[Dict[str, Any]]

class WebsocketsUpdateResponse(BaseModel):
    msg: str
    status: Status
