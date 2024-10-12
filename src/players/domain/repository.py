from abc import ABC, abstractmethod
from typing import Optional

from src.players.domain.models import Player, PlayerCreationRequest


class PlayerRepository(ABC):
    @abstractmethod
    def create(self, player: PlayerCreationRequest) -> Player:
        pass

    @abstractmethod
    def get(self, playerID: int) -> Optional[Player]:
        pass

    @abstractmethod
    def update(self, player: Player) -> None:
        pass

    @abstractmethod
    def delete(self, playerID: int) -> None:
        pass
