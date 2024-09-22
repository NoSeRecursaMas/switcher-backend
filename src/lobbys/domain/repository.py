from abc import ABC, abstractmethod
from src.lobbys.domain.models import LobbyResponse, CreteLobbyRequest


class LobbyRepository(ABC):
    @abstractmethod
    def save(self, lobby: CreteLobbyRequest) -> LobbyResponse:
        pass
