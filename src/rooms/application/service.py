from typing import Optional
from fastapi import WebSocket

from src.players.domain.repository import PlayerRepository
from src.players.domain.service import RepositoryValidators as PlayerRepositoryValidators
from src.rooms.domain.models import RoomCreationRequest, RoomID
from src.rooms.domain.repository import RoomRepositoryWS
from src.rooms.domain.service import RepositoryValidators as RoomRepositoryValidators


class RoomService:
    def __init__(
        self,
        room_repository: RoomRepositoryWS,
        player_repository: Optional[PlayerRepository] = None,
    ):
        self.room_repository = room_repository

        self.room_domain_service = RoomRepositoryValidators(room_repository, player_repository)
        self.player_domain_service = PlayerRepositoryValidators(player_repository)

    async def create_room(self, room_data: RoomCreationRequest) -> RoomID:
        await self.player_domain_service.validate_player_exists(room_data.playerID)

        saved_room = self.room_repository.create(room_data)
        self.room_repository.add_player_to_room(playerID=room_data.playerID, roomID=saved_room.roomID)
        await self.room_repository.broadcast_status_room_list()

        return saved_room

    async def leave_room(self, roomID: int, playerID: int) -> None:
        await self.player_domain_service.validate_player_exists(playerID)
        await self.room_domain_service.validate_room_exists(roomID)
        await self.room_domain_service.validate_player_in_room(playerID, roomID)
        self.room_domain_service.validate_player_is_not_owner(playerID, roomID)

        self.room_repository.remove_player_from_room(playerID=playerID, roomID=roomID)

        await self.room_repository.broadcast_status_room_list()
        await self.room_repository.broadcast_status_room(roomID)

    async def join_room(self, roomID: int, playerID: int) -> None:
        await self.player_domain_service.validate_player_exists(playerID)
        await self.room_domain_service.validate_room_exists(roomID)
        self.room_domain_service.validate_room_full(roomID)

        self.room_repository.add_player_to_room(playerID=playerID, roomID=roomID)

        await self.room_repository.broadcast_status_room_list()
        await self.room_repository.broadcast_status_room(roomID)

    async def connect_to_room_list_websocket(self, playerID: int, websocket: WebSocket) -> None:
        await self.player_domain_service.validate_player_exists(playerID, websocket)

        await self.room_repository.setup_connection_room_list(websocket)

    async def connect_to_room_websocket(self, playerID: int, roomID: int, websocket: WebSocket) -> None:
        await self.player_domain_service.validate_player_exists(playerID, websocket)
        await self.room_domain_service.validate_room_exists(roomID, websocket)
        await self.room_domain_service.validate_player_in_room(playerID, roomID, websocket)

        await self.room_repository.setup_connection_room(playerID, roomID, websocket)        
