from src.lobbys.domain.repository import LobbyRepository
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest, GetLobbyResponse
from sqlalchemy.orm import Session
from src.lobbys.infrastructure.models import Lobby, PlayerLobby
from src.players.infrastructure.models import Player


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

    def save_lobby_player(self, lobbyID: int, playerID: int):

        player_lobby_entry = PlayerLobby(lobbyID=lobbyID, playerID=playerID)
        self.db.add(player_lobby_entry)
        self.db.commit()

    def get_all(self) -> list[GetLobbyResponse]:
        
        lobbies_all = self.db.query(Lobby).order_by(Lobby.lobbyID).all()
        lobbies_list = []
        
        for lobby in lobbies_all:
            lobby_infra = GetLobbyResponse(lobbyID=lobby.lobbyID,
                                           roomName=lobby.name,
                                           maxPlayers=lobby.max_players,
                                           actualPlayers=self.get_actual_players(lobby.lobbyID),
                                           started=False,
                                           private= not lobby.password 
                                           )
            lobbies_list.append(lobby_infra)
            
        return lobbies_list
    
    def get_actual_players(self, lobbyID: int) -> int:
        lobby = self.db.query(Lobby).filter(Lobby.lobbyID == lobbyID).first()    
        return len(lobby.players)
        