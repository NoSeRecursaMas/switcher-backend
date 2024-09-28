from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class LobbyResponse(BaseModel):
    lobbyID: int

class CreateLobbyRequest(BaseModel):
    owner: int
    name: str
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
    password: str = None

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
    players: list[dict[str, str]]

