from pydantic import BaseModel


class LobbyResponse(BaseModel):
    lobbyID: int


class CreteLobbyRequest(BaseModel):
    owner: int
    lobbyName: str
    min_players: int
    max_players: int
    password: str = None
