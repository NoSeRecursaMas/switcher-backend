from src.lobbys.domain.repository import LobbyRepository
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest
from sqlalchemy.orm import Session
from src.lobbys.infrastructure.models import Lobby


class SQLAlchemyRepository(LobbyRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, lobby: CreateLobbyRequest) -> LobbyResponse:

        lobby_infra = Lobby(name=lobby.name,
                            min_players=lobby.min_players,
                            max_players=lobby.max_players,
                            password=lobby.password,
                            owner=lobby.owner
                            )

        self.db.add(lobby_infra)
        self.db.commit()
        self.db.refresh(lobby_infra)

        return LobbyResponse(lobbyID=lobby_infra.lobbyID)
