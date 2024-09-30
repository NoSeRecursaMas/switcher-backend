from pydantic import BaseModel


class PlayerResponse(BaseModel):
    playerID: int
    username: str


class PlayerUsername(BaseModel):
    username: str

class PlayerID(BaseModel):
    playerID: int

class PlayerID(BaseModel):
    playerID: int


class PlayerLobby(BaseModel):
    playerID: int
    roomID: int
