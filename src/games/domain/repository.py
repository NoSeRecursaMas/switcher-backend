from abc import ABC, abstractmethod
from typing import Optional, Dict, Union, List

from src.games.domain.models import (
    Game,
    GameCreationRequest,
    GameID,
)

class GameRepository(ABC):
    @abstractmethod
    def create(self, roomID: int, board: List[Dict[str, Union[int, str]]]) -> GameID:
        pass

    @abstractmethod    
    def create_figure_cards(self, roomID: int) -> None:
        pass

    @abstractmethod
    def get(self, gameID: int) -> Optional[Game]:
        pass

    @abstractmethod
    def delete(self, gameID: int) -> None:
        pass

    @abstractmethod
    def is_player_in_game(self, gameID: int, playerID: int) -> bool:
        pass

