from abc import ABC, abstractmethod
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest


class LobbyRepository(ABC):
    @abstractmethod
    def save(self, lobby: CreateLobbyRequest) -> LobbyResponse:
        pass
