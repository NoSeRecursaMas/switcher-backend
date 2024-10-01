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

    def leave_room(self, roomID: int, playerID: int) -> None:

        self.domain_service.validate_player_exists(playerID)
        self.domain_service.validate_room_exists(roomID)
        self.domain_service.validate_player_in_room(playerID, roomID)
        self.domain_service.validate_player_is_not_owner(playerID)

        self.room_repository.disassociate_player_from_room(
            playerID=playerID, roomID=roomID)

    def get_all_rooms(self):
        return self.room_repository.get_all_rooms()

    def get_public_info(self, roomID):
        return self.room_repository.get_public_info(roomID)
