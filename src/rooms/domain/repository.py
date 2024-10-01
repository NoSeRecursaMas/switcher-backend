from abc import ABC, abstractmethod
from src.rooms.domain.models import RoomID, RoomCreationRequest, RoomExtendedInfo, RoomPublicInfo


class RoomRepository(ABC):
    @abstractmethod
    def create(self, room: RoomCreationRequest) -> RoomID:
        pass

    @abstractmethod
    def get(self, roomID: int) -> RoomPublicInfo:
        pass

    @abstractmethod
    def get_public_info(self, roomID: int) -> RoomPublicInfo:
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
    def delete(self, playerID: int) -> None:
        pass

    @abstractmethod
    def associate_player_from_room(self, playerID: int, roomID: int) -> None:
        pass

    @abstractmethod
    def disassociate_player_from_room(self, playerID: int, roomID: int) -> None:
        pass

    @abstractmethod
    def is_owner(self, playerID: int) -> bool:
        pass

    @abstractmethod
    def is_player_in_room(self, playerID: int, roomID: int) -> bool:
        pass
