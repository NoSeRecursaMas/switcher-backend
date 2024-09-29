from abc import ABC, abstractmethod
from typing import Union
from src.players.domain.models import PlayerResponse


class PlayerRepository(ABC):
    @abstractmethod
    def save(self, player: PlayerResponse) -> None:
        pass

    @abstractmethod
    def find(self, playerID: int) -> Union[PlayerResponse, None]:
        pass
