from abc import ABC, abstractmethod
from src.players.domain.model import Player


class PlayerRepository(ABC):
    @abstractmethod
    def save(self, player: Player) -> None:
        pass