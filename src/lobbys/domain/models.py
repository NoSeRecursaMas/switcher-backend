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
    lobbyID: int
    roomName: str
    maxPlayers: int
    actualPlayers: int
    #started: bool
    private: bool

