from src.rooms.domain.repository import RoomRepository
from src.rooms.domain.models import Room as RoomDomain, RoomID, RoomCreationRequest, RoomExtendedInfo, RoomPublicInfo
from sqlalchemy.orm import Session
from src.rooms.infrastructure.models import Room, PlayerRoom
from src.players.infrastructure.models import Player
from typing import List


class SQLAlchemyRepository(RoomRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, room: RoomCreationRequest) -> RoomID:

        room = Room(
            name=room.roomName,
            minPlayers=room.minPlayers,
            maxPlayers=room.maxPlayers,
            password=room.password,
            hostID=room.playerID
        )

        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)

        return RoomID(roomID=room.roomID)

    def get(self, room_id: int) -> RoomDomain:
        room = self.db.query(Room).filter(Room.roomID == room_id).first()

        if room is None:
            return None

        players = self.db.query(Player).join(PlayerRoom).filter(
            PlayerRoom.roomID == room_id).all()

        players_list = [{"playerID": str(
            player.playerID), "username": player.username} for player in players]

        return Room(
            roomID=room.roomID,
            roomName=room.name,
            minPlayers=room.minPlayers,
            maxPlayers=room.maxPlayers,
            hostID=room.hostID,
            hash_password=room.password,
            players=players_list
        )

    def get_public_info(self, room_id) -> RoomPublicInfo:
        room = self.db.query(Room).filter(Room.roomID == room_id).first()
        if room is None:
            return None

        players = self.db.query(Player).join(PlayerRoom).filter(
            PlayerRoom.roomID == room_id).all()

        players_list = [{"playerID": str(
            player.playerID), "username": player.username} for player in players]

        room_data = RoomPublicInfo(
            hostID=room.hostID,
            roomName=room.name,
            roomID=room.roomID,
            minPlayers=room.minPlayers,
            maxPlayers=room.maxPlayers,
            players=players_list
        )
        return room_data

    def get_all_rooms(self) -> List[RoomExtendedInfo]:
        all_rooms = self.db.query(Room).order_by(Room.roomID).all()
        room_list = []

        for room in all_rooms:
            room_info = RoomExtendedInfo(
                roomID=room.roomID,
                roomName=room.name,
                maxPlayers=room.maxPlayers,
                actualPlayers=self.get_player_count(room.roomID),
                started=False,
                private=room.password is not None
            )
            room_list.append(room_info)

        return room_list

    def get_player_count(self, roomID: int) -> int:
        players = self.db.query(PlayerRoom).filter(
            PlayerRoom.roomID == roomID).all()
        return len(players)

    def update(self, room: Room) -> None:
        self.db.query(Room).filter(Room.roomID == room.roomID).update(
            {"name": room.roomName, "minPlayers": room.minPlayers, "maxPlayers": room.maxPlayers})
        self.db.commit()

    def delete(self, room_id: int) -> None:
        self.db.query(Room).filter(Room.roomID == room_id).delete()
        self.db.commit()

    def associate_player_from_room(self, roomID: int, playerID: int):

        player_join_room = PlayerRoom(roomID=roomID, playerID=playerID)
        self.db.add(player_join_room)
        self.db.commit()

    def disassociate_player_from_room(self, player_id: int, room_id: int) -> None:

        player_in_room = self.db.query(PlayerRoom).filter(
            PlayerRoom.playerID == player_id,
            PlayerRoom.roomID == room_id
        )
        player_in_room.delete()
        self.db.commit()

    def is_owner(self, player_id: int) -> bool:
        room = self.db.query(Room).filter(
            Room.hostID == player_id).first()
        return room is not None

    def is_player_in_room(self, playerID: int, roomID: int) -> bool:
        player_in_room = self.db.query(PlayerRoom).filter_by(
            playerID=playerID, roomID=roomID).first()
        return player_in_room is not None
