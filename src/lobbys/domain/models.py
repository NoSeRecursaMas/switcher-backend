from pydantic import BaseModel


class LobbyResponse(BaseModel):
    lobbyID: int


class CreateLobbyRequest(BaseModel):
    owner: int
    name: str
    min_players: int
    max_players: int
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