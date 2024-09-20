from pydantic import BaseModel


class LobbyResponse(BaseModel):
    lobbyID: int


class CreteLobbyRequest(BaseModel):
    plyerID: int
    roomName: str
    minPlayers: int
    maxPlayers: int
    password: str
