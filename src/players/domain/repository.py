from abc import ABC, abstractmethod
from src.players.domain.models import PlayerResponse, PlayerUsername


class PlayerRepository(ABC):
    @abstractmethod
    def save(self, player: PlayerUsername) -> PlayerResponse:
        pass
