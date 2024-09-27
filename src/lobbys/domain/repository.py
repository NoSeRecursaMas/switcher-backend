from abc import ABC, abstractmethod
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest
from src.players.domain.models import PlayerID


class LobbyRepository(ABC):
    @abstractmethod
    def save(self, lobby: CreateLobbyRequest) -> LobbyResponse:
        pass

    @abstractmethod
    def delete(self, player_id: int) -> None:
        pass

    @abstractmethod
    def remove_player_lobby_association(self, player_id: int = None, lobby_id: int = None) -> None:
        pass

    @abstractmethod
    def is_owner(self, player_id: int) -> bool:
        pass

    @abstractmethod
    def save_lobby_player(self, playerID: int, lobbyID: int) -> None:
        pass

    @abstractmethod
    def player_in_lobby(self, playerID: int, lobbyID: int) -> bool:
        pass
