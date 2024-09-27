from src.lobbys.domain.repository import LobbyRepository
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest
from sqlalchemy.orm import Session
from src.lobbys.infrastructure.models import Lobby
from src.lobbys.infrastructure.models import PlayerLobby


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
        
    def delete(self, lobby_id: int) -> None:
        self.db.query(Lobby).filter(Lobby.lobbyID == lobby_id).delete()
        self.db.commit()

    def remove_player_lobby_association(self, player_id: int = None, lobby_id: int = None) -> None:
        query = self.db.query(PlayerLobby)

        if player_id:
            query = query.filter(PlayerLobby.playerID == player_id)
        
        if lobby_id:
            query = query.filter(PlayerLobby.lobbyID == lobby_id)
        
        query.delete()
        self.db.commit()

    def is_owner(self, player_id: int) -> bool:
        lobby = self.db.query(Lobby).filter(Lobby.owner == player_id).first()
        return lobby is not None