from src.rooms.domain.models import RoomID, RoomCreationRequest
from src.rooms.domain.service import RepositoryValidators
from src.rooms.domain.repository import RoomRepository
from src.players.domain.repository import PlayerRepository


class RoomService():
    def __init__(self, room_repository: RoomRepository, player_repository: PlayerRepository = None):
        self.room_repository = room_repository
        self.domain_service = RepositoryValidators(
            player_repository, room_repository)

    def create_room(self, room_data: RoomCreationRequest) -> RoomID:
        self.domain_service.validate_player_exists(room_data.playerID)

        saved_room = self.room_repository.create(room_data)
        self.room_repository.associate_player_from_room(
            saved_room.roomID, room_data.playerID)

        return saved_room

    def leave_room(self, room_id: int, player_id: int) -> None:

        self.domain_service.validate_player_exists(player_id)
        self.domain_service.validate_room_exists(room_id)
        self.domain_service.validate_player_in_room(player_id, room_id)
        self.domain_service.validate_player_is_not_owner(player_id)

        self.room_repository.disassociate_player_from_room(
            player_id=player_id, room_id=room_id)

    def get_all_rooms(self):
        return self.room_repository.get_all_rooms()

    def get_public_info(self, room_id):
        return self.room_repository.get_public_info(room_id)
