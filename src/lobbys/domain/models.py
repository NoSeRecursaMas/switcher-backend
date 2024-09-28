from pydantic import BaseModel
from typing import Optional


class LobbyResponse(BaseModel):
    roomID: int


class CreateLobbyRequest(BaseModel):
    playerID: int
    roomName: str
    minPlayers: int
    maxPlayers: int
    password: Optional[str] = None


'''
    owner: int
    name: str
    minPlayers: int
    maxPlayers: int
    password: str = None
'''


class GetLobbyResponse(BaseModel):
    roomID: int
    roomName: str
    maxPlayers: int
    actualPlayers: int
    started: bool
    private: bool
