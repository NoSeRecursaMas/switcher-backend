from abc import ABC, abstractmethod
from typing import Optional

from fastapi.websockets import WebSocket

from src.rooms.domain.models import (
    RoomCreationRequest,
    RoomExtendedInfo,
    RoomID,
    RoomPublicInfo,
)


class RoomRepository(ABC):
    @abstractmethod
    def create(self, room: RoomCreationRequest) -> RoomID:
        pass

    @abstractmethod
    def get(self, roomID: int) -> Optional[RoomPublicInfo]:
        pass

    @abstractmethod
    def get_public_info(self, roomID: int) -> Optional[RoomPublicInfo]:
        pass

    @abstractmethod
    def get_all_rooms(self) -> list[RoomExtendedInfo]:
        pass

    @abstractmethod
    def get_player_count(self, roomID: int) -> int:
        pass

    @abstractmethod
    def update(self, room: RoomPublicInfo) -> None:
        pass

    @abstractmethod
    def delete_and_clean(self, roomID: int) -> None:
        pass

    @abstractmethod
    def add_player_to_room(self, playerID: int, roomID: int) -> None:
        pass

    @abstractmethod
    def remove_player_from_room(self, playerID: int, roomID: int) -> None:
        pass

    @abstractmethod
    def is_owner(self, playerID: int, roomID: int) -> bool:
        pass

    @abstractmethod
    def is_player_in_room(self, playerID: int, roomID: int) -> bool:
        pass

    @abstractmethod
    def is_game_started(self, roomID: int) -> bool:
        pass

    @abstractmethod
    def set_position(self, playerID: int, position: int, roomID: int) -> None:
        pass

    @abstractmethod
    def get_first_turn(self, roomID: int) -> int:
        pass

    @abstractmethod
    def get_turn(self, roomID: int, posEnabled) -> int:
        pass


class RoomRepositoryWS(RoomRepository):
    @abstractmethod
    async def setup_connection_room_list(self, websocket: WebSocket) -> None:
        pass

    @abstractmethod
    async def setup_connection_room(self, playerID: int, roomID: int, websocket: WebSocket) -> None:
        pass

    @abstractmethod
    async def broadcast_status_room_list(self) -> None:
        pass

    @abstractmethod
    async def broadcast_status_room(self, roomID: int) -> None:
        pass

    @abstractmethod
    async def broadcast_start_game(self, roomID: int, gameID: int) -> None:
        pass

    @abstractmethod
    async def broadcast_room_cancellation(self, roomID: int) -> None:
        pass

    @abstractmethod
    async def disconnect_player(self, playerID: int, roomID: int) -> None:
        pass
