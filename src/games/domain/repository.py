from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

from fastapi.websockets import WebSocket

from src.games.domain.models import (
    Game,
    GameID,
    GamePublicInfo,
)
from src.players.domain.models import Player as PlayerDomain


class GameRepository(ABC):
    @abstractmethod
    def create(self, roomID: int, board: List[Dict[str, Union[int, str]]]) -> GameID:
        pass

    @abstractmethod
    def create_figure_cards(self, gameID: int) -> None:
        pass

    @abstractmethod
    def create_movement_cards(self, gameID: int) -> None:
        pass

    @abstractmethod
    def get(self, gameID: int) -> Optional[Game]:
        pass

    @abstractmethod
    def delete(self, gameID: int) -> None:
        pass

    @abstractmethod
    def get_players(self, gameID: int) -> List[PlayerDomain]:
        pass

    @abstractmethod
    def is_player_in_game(self, playerID: int, gameID: int) -> bool:
        pass

    @abstractmethod
    def get_public_info(self, gameID: int, playerID: int) -> GamePublicInfo:
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

    @abstractmethod
    def get_current_turn(self, gameID: int) -> int:
        pass

    @abstractmethod
    def get_position_player(self, gameID: int, playerID: int) -> int:
        pass
    
class GameRepositoryWS(GameRepository):
    @abstractmethod
    async def setup_connection_game(self, playerID: int, gameID: int, websocket: WebSocket) -> None:
        pass

    @abstractmethod
    async def broadcast_status_game(self, gameID: int) -> None:
        pass
