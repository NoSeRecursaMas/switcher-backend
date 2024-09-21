from src.lobbys.domain.models import LobbyResponse, CreteLobbyRequest
from src.lobbys.domain.service import DomaineService
from src.lobbys.domain.repository import LobbyRepository
from src.players.domain.repository import PlayerRepository


class LobbyService():
    def __init__(self, repository: LobbyRepository, player_repository: PlayerRepository):
        self.repository = repository
        self.domain_service = DomaineService(player_repository)

    def create_lobby(self, lobby_data: CreteLobbyRequest) -> LobbyResponse:

        DomaineService.validate_lobby_name(lobby_data.lobbyName)
        self.domain_service.validate_owner_exist(lobby_data.owner)

        saved_lobby = self.repository.save(lobby_data)

        return saved_lobby
