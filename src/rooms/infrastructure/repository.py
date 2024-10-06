from typing import List, Optional

from sqlalchemy.orm import Session

from src.players.infrastructure.models import Player
from src.players.domain.models import Player as PlayerDomain
from src.rooms.domain.models import Room as RoomDomain
from src.rooms.domain.models import (
    RoomCreationRequest,
    RoomExtendedInfo,
    RoomID,
    RoomPublicInfo,
)
from src.rooms.domain.repository import RoomRepository
from src.rooms.infrastructure.models import PlayerRoom, Room


class SQLAlchemyRepository(RoomRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, room: RoomCreationRequest) -> RoomID:
        room = Room(
            roomName=room.roomName,
            minPlayers=room.minPlayers,
            maxPlayers=room.maxPlayers,
            password=room.password,
            hostID=room.playerID,
        )

        self.db_session.add(room)
        self.db_session.commit()
        self.db_session.refresh(room)

        return RoomID(roomID=room.roomID)

    def get(self, roomID: int) -> Optional[RoomDomain]:
        room = self.db_session.query(Room).filter(Room.roomID == roomID).first()

        if room is None:
            return None

        players = self.db_session.query(Player).join(PlayerRoom).filter(PlayerRoom.roomID == roomID).all()

        players_list = [PlayerDomain(playerID=player.playerID, username=player.username) for player in players]

        return RoomDomain(
            roomID=room.roomID,
            roomName=room.roomName,
            minPlayers=room.minPlayers,
            maxPlayers=room.maxPlayers,
            hostID=room.hostID,
            password=room.password,
            players=players_list,
        )

    def get_public_info(self, roomID) -> Optional[RoomPublicInfo]:
        room = self.db_session.query(Room).filter(Room.roomID == roomID).first()
        if room is None:
            return None

        players = self.db_session.query(Player).join(PlayerRoom).filter(PlayerRoom.roomID == roomID).all()

        players_list = [{"playerID": str(player.playerID), "username": player.username} for player in players]

        room_data = RoomPublicInfo(
            hostID=room.hostID,
            roomName=room.roomName,
            roomID=room.roomID,
            minPlayers=room.minPlayers,
            maxPlayers=room.maxPlayers,
            players=players_list,
        )
        return room_data

    def get_all_rooms(self) -> List[RoomExtendedInfo]:
        all_rooms = self.db_session.query(Room).order_by(Room.roomID).all()
        room_list = []

        for room in all_rooms:
            room_info = RoomExtendedInfo(
                roomID=room.roomID,
                roomName=room.roomName,
                maxPlayers=room.maxPlayers,
                actualPlayers=self.get_player_count(room.roomID),
                started=False,
                private=room.password is not None,
            )
            room_list.append(room_info)

        return room_list

    def get_player_count(self, roomID: int) -> int:
        players = self.db_session.query(PlayerRoom).filter(PlayerRoom.roomID == roomID).all()
        return len(players)
    
    def get_players(self, roomID: int) -> List[PlayerDomain]:
        players = self.db_session.query(Room).filter(Room.roomID == roomID).first().players
        return [PlayerDomain(playerID=player.playerID, username=player.username) for player in players]

    def update(self, room: Room) -> None:
        self.db_session.query(Room).filter(Room.roomID == room.roomID).update(
            {
                "roomName": room.roomName,
                "minPlayers": room.minPlayers,
                "maxPlayers": room.maxPlayers,
            }
        )
        self.db_session.commit()

    def delete(self, roomID: int) -> None:
        self.db_session.query(Room).filter(Room.roomID == roomID).delete()
        self.db_session.commit()

    def associate_player_from_room(self, playerID: int, roomID: int) -> None:
        player_join_room = PlayerRoom(roomID=roomID, playerID=playerID)
        self.db_session.add(player_join_room)
        self.db_session.commit()

    def disassociate_player_from_room(self, playerID: int, roomID: int) -> None:
        player_in_room = self.db_session.query(PlayerRoom).filter(
            PlayerRoom.playerID == playerID, PlayerRoom.roomID == roomID
        )
        player_in_room.delete()
        self.db_session.commit()

    def is_owner(self, playerID: int) -> bool:
        room = self.db_session.query(Room).filter(Room.hostID == playerID).first()
        return room is not None

    def is_player_in_room(self, playerID: int, roomID: int) -> bool:
        player_in_room = self.db_session.query(PlayerRoom).filter_by(playerID=playerID, roomID=roomID).first()
        return player_in_room is not None
