from pydantic import BaseModel


class PlayerResponse(BaseModel):
    playerID: int
    username: str


class PlayerUsername(BaseModel):
    username: str


class PlayerLobby(BaseModel):
    playerID: int
    lobbyID: int
