from typing import Optional

from src.players.domain.repository import PlayerRepository
from src.players.domain.service import (
    RepositoryValidators as PlayerRepositoryValidators,
)
from src.rooms.domain.models import RoomCreationRequest, RoomID, RoomPublicInfo
from src.rooms.domain.repository import RoomRepository
from src.rooms.domain.service import RepositoryValidators as RoomRepositoryValidators


class RoomService:
    def __init__(
        self,
        room_repository: RoomRepository,
        player_repository: Optional[PlayerRepository] = None,
    ):
        self.room_repository = room_repository

        if player_repository is not None:
            self.domain_service = RoomRepositoryValidators(room_repository, player_repository)
            self.player_domain_service = PlayerRepositoryValidators(player_repository)
        if player_repository is None:
            self.domain_service = RoomRepositoryValidators(room_repository)

    def create_room(self, room_data: RoomCreationRequest) -> RoomID:
        self.player_domain_service.validate_player_exists(room_data.playerID)

        saved_room = self.room_repository.create(room_data)
        self.room_repository.associate_player_from_room(saved_room.roomID, room_data.playerID)

        return saved_room

    def leave_room(self, roomID: int, playerID: int) -> None:
        self.player_domain_service.validate_player_exists(playerID)
        self.domain_service.validate_room_exists(roomID)
        self.domain_service.validate_player_in_room(playerID, roomID)
        self.domain_service.validate_player_is_not_owner(playerID)

        self.room_repository.disassociate_player_from_room(playerID=playerID, roomID=roomID)

    def get_all_rooms(self):
        return self.room_repository.get_all_rooms()

    def get_public_info(self, roomID: int) -> Optional[RoomPublicInfo]:
        return self.room_repository.get_public_info(roomID)
