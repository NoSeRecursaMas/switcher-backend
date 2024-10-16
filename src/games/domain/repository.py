from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import numpy as np

from fastapi.websockets import WebSocket

from src.games.domain.models import (
    Game,
    GameID,
    GamePublicInfo,
    BoardPiecePosition,
    FigureCard,
    BoardPiece,
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
    def set_player_inactive(self, playerID: int, gameID: int) -> None:
        pass

    @abstractmethod
    def is_player_active(self, playerID: int, gameID: int) -> bool:
        pass

    @abstractmethod
    def get_active_players(self, gameID: int) -> List[PlayerDomain]:
        pass

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

    @abstractmethod
    def delete_and_clean(self, gameID: int) -> None:
        pass

    @abstractmethod
    def get_figure_card(self, figureCardID: int) -> Optional[FigureCard]:
        pass

    @abstractmethod
    def play_figure(self, figureID: int) -> None:
        pass

    @abstractmethod
    def get_board(self, gameID: int) -> List[BoardPiece]:
        pass

    @abstractmethod
    def check_border_validity(self, positions: List[BoardPiecePosition], layer: np.ndarray) -> bool:
        pass


class GameRepositoryWS(GameRepository):
    @abstractmethod
    async def setup_connection_game(self, playerID: int, gameID: int, websocket: WebSocket) -> None:
        pass

    @abstractmethod
    async def broadcast_status_game(self, gameID: int) -> None:
        pass

    @abstractmethod
    async def broadcast_end_game(self, gameID: int, winnerID: int) -> None:
        pass

    @abstractmethod
    async def remove_player(self, playerID: int, gameID: int) -> None:
        pass
