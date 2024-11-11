from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Union

import numpy as np
from fastapi.websockets import WebSocket

from src.games.domain.models import (
    BoardPiece,
    BoardPiecePosition,
    FigureCard,
    Game,
    GameID,
    GamePublicInfo,
)
from src.games.domain.models import MovementCard as MovementCardDomain
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
    def play_movement(
        self, gameID: int, card_id: int, originX: int, originY: int, destinationX: int, destinationY: int
    ) -> None:
        pass

    @abstractmethod
    def is_player_turn(self, playerID: int, gameID: int) -> bool:
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

    @abstractmethod
    def skip(self, gameID: int) -> int:
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
    def play_figure(self, gameID: int, figureID: int, figure: List[BoardPiecePosition]) -> None:
        pass

    @abstractmethod
    def get_board(self, gameID: int) -> List[BoardPiece]:
        pass

    @abstractmethod
    def check_border_validity(self, positions: List[BoardPiecePosition], layer: np.ndarray) -> bool:
        pass

    @abstractmethod
    def get_movement_card(self, cardID: int) -> MovementCardDomain:
        pass

    @abstractmethod
    def has_movement_card(self, playerID: int, cardID: int) -> bool:
        pass

    @abstractmethod
    def card_exists(self, cardID: int) -> bool:
        pass

    @abstractmethod
    def delete_partial_movement(self, gameID: int) -> None:
        pass

    @abstractmethod
    def partial_movement_exists(self, gameID: int) -> bool:
        pass

    @abstractmethod
    def clean_partial_movements(self, gameID: int) -> None:
        pass

    @abstractmethod
    def was_card_used_in_partial_movement(self, gameID: int, cardID: int) -> bool:
        pass

    @abstractmethod
    def set_partial_movements_to_empty(self, gameID: int) -> None:
        pass

    @abstractmethod
    def desvinculate_partial_movement_cards(self, gameID: int) -> None:
        pass

    @abstractmethod
    def get_prohibited_color(self, gameID: int) -> str:
        pass

    @abstractmethod
    def is_blocked_and_last_card(self, gameID: int, figureID: int) -> bool:
        pass

    @abstractmethod
    def figure_card_count(self, gameID: int, playerID: int) -> int:
        pass

    @abstractmethod
    def block_managment(self, gameID: int, figureID: int, figure: List[BoardPiecePosition]) -> None:
        pass

    @abstractmethod
    def unblock_managment(self, gameID: int, blockedcardID: int) -> None:
        pass

    @abstractmethod
    def is_not_blocked(self, cardID) -> bool:
        pass

    @abstractmethod
    def get_blocked_card(self, gameID: int, playerID: int) -> Optional[int]:
        pass

    @abstractmethod
    def card_was_blocked(self, cardID: int) -> bool:
        pass

    @abstractmethod
    def set_was_blocked_false(self, cardID: int) -> None:
        pass

    @abstractmethod
    def has_three_cards(self, gameID: int, playerID: int) -> bool:
        pass


    @abstractmethod
    def get_current_timestamp_next_turn(self, gameID: int) -> datetime:
        pass

    @abstractmethod
    def set_timestamp_next_turn(self, gameID: int, timestamp: datetime) -> None:
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

    @abstractmethod
    async def send_log_play_movement_card(self, gameID: int, playerID: int, cardID: int) -> None:
        pass

    @abstractmethod
    async def send_log_cancel_movement_card(self, gameID: int, playerID: int) -> None:
        pass

    @abstractmethod
    async def send_log_player_leave_game(self, gameID: int, playerID: int) -> None:
        pass

    @abstractmethod
    async def send_log_play_figure(self, gameID: int, playerID: int, figureID: int) -> None:
        pass

    @abstractmethod
    async def send_log_block_figure(self, gameID: int, playerID: int, targetID: int, figureID: int) -> None:
        pass

    @abstractmethod
    async def send_log_turn_skip(self, gameID: int, playerID: int, auto: bool) -> None:
        pass
