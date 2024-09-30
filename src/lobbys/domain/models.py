from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from typing import Optional
from typing import List

class LobbyResponse(BaseModel):
    roomID: int


class CreateLobbyRequest(BaseModel):
    playerID: int
    roomName: str
    minPlayers: int
    maxPlayers: int
    password: Optional[str] = None


class RoomInfo(BaseModel):
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


class GetLobbyResponse(BaseModel):
    roomID: int
    roomName: str
    maxPlayers: int
    actualPlayers: int
    started: bool
    private: bool


class GetLobbyData(BaseModel):
    hostID: int
    roomName: str
    roomID: int
    minPlayers: int
    maxPlayers: int
    players: List[dict[str, str]]

