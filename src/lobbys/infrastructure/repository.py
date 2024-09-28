from src.lobbys.domain.repository import LobbyRepository
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest, GetLobbyResponse, GetLobbyData
from sqlalchemy.orm import Session
from src.lobbys.infrastructure.models import Lobby, PlayerLobby
from src.players.infrastructure.models import Player


class SQLAlchemyRepository(LobbyRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, lobby: CreateLobbyRequest) -> LobbyResponse:

        lobby_infra = Lobby(name=lobby.roomName,
                            minPlayers=lobby.minPlayers,
                            maxPlayers=lobby.maxPlayers,
                            password=lobby.password,
                            owner=lobby.playerID
                            )

        self.db.add(lobby_infra)
        self.db.commit()
        self.db.refresh(lobby_infra)

        return LobbyResponse(roomID=lobby_infra.roomID)

    def save_lobby_player(self, roomID: int, playerID: int):

        player_lobby_entry = PlayerLobby(roomID=roomID, playerID=playerID)
        self.db.add(player_lobby_entry)
        self.db.commit()

    def get_all(self) -> list[GetLobbyResponse]:

        lobbies_all = self.db.query(Lobby).order_by(Lobby.roomID).all()
        lobbies_list = []

        for lobby in lobbies_all:
            lobby_infra = GetLobbyResponse(roomID=lobby.roomID,
                                           roomName=lobby.name,
                                           maxPlayers=lobby.maxPlayers,
                                           actualPlayers=self.get_actual_players(
                                               lobby.roomID),
                                           started=False,
                                           private=not lobby.password
                                           )
            lobbies_list.append(lobby_infra)

        return lobbies_list

    def get_actual_players(self, roomID: int) -> int:
        players = self.db.query(PlayerLobby).filter(
            PlayerLobby.roomID == roomID).all()
        return len(players)
        
    def get_data_lobby(self, lobby_id) -> GetLobbyData:
        lobby = self.db.query(Lobby).filter(Lobby.lobbyID == lobby_id).first()
        players = self.db.query(Player).join(PlayerLobby).filter(PlayerLobby.lobbyID == lobby_id).all()
    
        players_list = [{"playerID": str(player.playerID), "username": player.username} for player in players]

        lobby_data = GetLobbyData(
            hostID=lobby.owner,
            roomName=lobby.name,
            roomID=lobby.lobbyID,
            minPlayers=lobby.min_players,
            maxPlayers=lobby.max_players,
            players=players_list
        )
    
        return lobby_data