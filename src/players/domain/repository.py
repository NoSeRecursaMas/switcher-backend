from abc import ABC, abstractmethod
from typing import Union
from src.players.domain.models import Player


class PlayerRepository(ABC):
    @abstractmethod
    def create(self, player: Player) -> None:
        pass

    @abstractmethod
    def get(self, playerID: int) -> Union[Player, None]:
        pass

    @abstractmethod
    def update(self, player: Player) -> None:
        pass

    @abstractmethod
    def delete(self, playerID: int) -> None:
        pass
