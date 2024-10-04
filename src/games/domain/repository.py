from abc import ABC, abstractmethod
from typing import Optional

from src.games.domain.models import (
    Game,
    GameCreationRequest,
    GameID,
)

class GameRepository(ABC):
    @abstractmethod
    def create(self, game: GameCreationRequest) -> GameID:
        pass

    @abstractmethod
    def get(self, gameID: int) -> Optional[Game]:
        pass

    @abstractmethod
    def delete(self, gameID: int) -> None:
        pass

    @abstractmethod
    def associate_player_from_game(self, gameID: int, playerID: int) -> None:
        pass

    @abstractmethod
    def disassociate_player_from_game(self, gameID: int, playerID: int) -> None:
        pass

    @abstractmethod
    def is_player_in_game(self, gameID: int, playerID: int) -> bool:
        pass