from abc import ABC, abstractmethod
from src.players.domain.models import PlayerResponse


class PlayerRepository(ABC):
    @abstractmethod
    def save(self, player: PlayerResponse) -> None:
        pass
