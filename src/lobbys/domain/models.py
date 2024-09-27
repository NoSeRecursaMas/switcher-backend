from pydantic import BaseModel


class LobbyResponse(BaseModel):
    lobbyID: int

class CreateLobbyRequest(BaseModel):
    owner: int
    name: str
    min_players: int
    max_players: int
    password: str = None
