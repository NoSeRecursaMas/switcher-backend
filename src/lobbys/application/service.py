from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest
from src.lobbys.domain.service import DomainService
from src.lobbys.domain.repository import LobbyRepository
from src.players.domain.repository import PlayerRepository



class LobbyService():
    def __init__(self, repository: LobbyRepository, player_repository: PlayerRepository = None):
        self.repository = repository
        self.domain_service = DomainService(player_repository, repository)

    def create_lobby(self, lobby_data: CreateLobbyRequest) -> LobbyResponse:

        DomainService.validate_lobby_name(lobby_data.roomName)
        DomainService.validate_player_count(
            lobby_data.minPlayers, lobby_data.maxPlayers)
        self.domain_service.validate_player_exists(lobby_data.playerID)

        saved_lobby = self.repository.save(lobby_data)
        self.repository.save_lobby_player(
            saved_lobby.roomID, lobby_data.playerID)

        return saved_lobby

    def leave_lobby(self, lobby_id: int, player_id: int) -> None:

        self.domain_service.validate_player_exists(player_id)
        self.domain_service.validate_lobby_exists(lobby_id)
        self.domain_service.validate_player_in_lobby(player_id, lobby_id)
        self.domain_service.validate_player_is_not_owner(player_id)

        self.repository.remove_player_lobby_association(player_id=player_id)

    def get_lobby(self):
        return self.repository.get_all()

    def get_data_lobby(self, lobby_id):
        return self.repository.get_data_lobby(lobby_id)

    def join_lobby(self,lobby_id: int, player_id: int) -> None:

        self.domain_service.validate_player_exists(player_id)
        self.domain_service.validate_lobby_exists(lobby_id)
        self.domain_service.validate_room_full(lobby_id)

        self.repository.save_lobby_player(lobby_id, player_id)