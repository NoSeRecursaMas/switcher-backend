from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest
from src.lobbys.domain.service import DomaineService
from src.lobbys.domain.repository import LobbyRepository
from src.players.domain.repository import PlayerRepository


class LobbyService():
    def __init__(self, repository: LobbyRepository, player_repository: PlayerRepository):
        self.repository = repository
        self.domain_service = DomaineService(player_repository)

    def create_lobby(self, lobby_data: CreateLobbyRequest) -> LobbyResponse:

        DomaineService.validate_lobby_name(lobby_data.name)
        print(lobby_data.max_players)
        DomaineService.validate_player_count(
            lobby_data.min_players, lobby_data.max_players)
        self.domain_service.validate_owner_exists(lobby_data.owner)

        saved_lobby = self.repository.save(lobby_data)

        return saved_lobby
