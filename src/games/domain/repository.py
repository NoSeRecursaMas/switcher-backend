from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

from src.games.domain.models import (
    Game,
    GameCreationRequest,
    GameID,
)
from src.players.domain.models import Player as PlayerDomain


class GameRepository(ABC):
    @abstractmethod
    def create(self, roomID: int, board: List[Dict[str, Union[int, str]]]) -> GameID:
        pass

    @abstractmethod
    def create_figure_cards(self, roomID: int, gameID: int) -> None:
        pass

    @abstractmethod
    def create_movement_cards(self, roomID: int, gameID: int) -> None:
        pass

    @abstractmethod
    def get(self, gameID: int) -> Optional[Game]:
        pass

    @abstractmethod
    def delete(self, gameID: int) -> None:
        pass

    @abstractmethod
    def get_game_players(self, gameID: int) -> List[PlayerDomain]:
        pass

    @abstractmethod
    def is_player_in_game(self, gameID: int, playerID: int) -> bool:
        pass

    @abstractmethod
    def skip(self, gameID: int) -> None:
        pass

    @abstractmethod
    def replacement_movement_card(self, gameID: int, playerID: int) -> None:
        pass

    @abstractmethod
    def replacement_figure_card(self, gameID: int, playerID: int) -> None:
        pass
    