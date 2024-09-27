from abc import ABC, abstractmethod

from typing import Union
from src.players.domain.models import PlayerResponse, PlayerUsername


class PlayerRepository(ABC):
    @abstractmethod
    def save(self, player: PlayerUsername) -> PlayerResponse:
        pass

    def find(self, playerID: int) -> Union[PlayerResponse, None]:
        pass