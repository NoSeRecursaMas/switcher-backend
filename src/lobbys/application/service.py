from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest
from src.lobbys.domain.service import DomainService
from src.lobbys.domain.repository import LobbyRepository
from src.players.domain.repository import PlayerRepository


class LobbyService():
    def __init__(self, repository: LobbyRepository, player_repository: PlayerRepository = None):
        self.repository = repository
        self.domain_service = DomainService(player_repository)

    def create_lobby(self, lobby_data: CreateLobbyRequest) -> LobbyResponse:

        DomainService.validate_lobby_name(lobby_data.roomName)
        DomainService.validate_player_count(
            lobby_data.minPlayers, lobby_data.maxPlayers)
        self.domain_service.validate_owner_exists(lobby_data.playerID)

        saved_lobby = self.repository.save(lobby_data)
        self.repository.save_lobby_player(
            saved_lobby.roomID, lobby_data.playerID)

        return saved_lobby

    def get_lobby(self):
        return self.repository.get_all()
