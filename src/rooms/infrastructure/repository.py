import json
from typing import List, Optional

import bcrypt
from fastapi.websockets import WebSocket
from sqlalchemy.orm import Session

from src.games.domain.models import GameID
from src.players.domain.models import Player
from src.rooms.domain.models import Room as RoomDomain
from src.rooms.domain.models import (
    RoomCreationRequest,
    RoomExtendedInfo,
    RoomID,
    RoomPublicInfo,
)
from src.rooms.domain.repository import RoomRepository, RoomRepositoryWS
from src.rooms.infrastructure.models import PlayerRoom, Room
from src.rooms.infrastructure.websocket import (
    MessageType,
    ws_manager_room,
    ws_manager_room_list,
)


class SQLAlchemyRepository(RoomRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, room: RoomCreationRequest) -> RoomID:
        encrypted_password = self.encrypt_password(room.password) if room.password else None

        room = Room(
            roomName=room.roomName,
            minPlayers=room.minPlayers,
            maxPlayers=room.maxPlayers,
            password=encrypted_password,
            hostID=room.playerID,
        )

        self.db_session.add(room)
        self.db_session.commit()
        self.db_session.refresh(room)

        return RoomID(roomID=room.roomID)

    def get(self, roomID: int) -> Optional[RoomDomain]:
        room = self.db_session.get(Room, roomID)

        if room is None:
            return None

        players_list = [Player(playerID=player.playerID, username=player.username) for player in room.players]

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
        room = self.get(roomID)

        if room is None:
            return None

        return RoomPublicInfo(
            roomID=room.roomID,
            roomName=room.roomName,
            minPlayers=room.minPlayers,
            maxPlayers=room.maxPlayers,
            hostID=room.hostID,
            players=room.players,
        )

    def get_all_rooms(self) -> List[RoomExtendedInfo]:
        all_rooms = self.db_session.query(Room).order_by(Room.roomID).all()
        room_list = [
            RoomExtendedInfo(
                roomID=room.roomID,
                roomName=room.roomName,
                minPlayers=room.minPlayers,
                maxPlayers=room.maxPlayers,
                actualPlayers=len(
                    [
                        player
                        for player in room.players
                        if self.db_session.query(PlayerRoom)
                        .filter_by(playerID=player.playerID, roomID=room.roomID)
                        .one()
                        .isActive
                    ]
                ),
                started=room.game is not None,
                private=room.password is not None,
                playersID=[
                    player.playerID
                    for player in room.players
                    if self.db_session.query(PlayerRoom)
                    .filter_by(playerID=player.playerID, roomID=room.roomID)
                    .one()
                    .isActive
                ],
            )
            for room in all_rooms
        ]

        return room_list

    def get_player_count(self, roomID: int) -> int:
        room = self.get(roomID)
        if room is None:
            raise ValueError(f"Room with ID {roomID} not found")
        return len(room.players)

    def get_players(self, roomID: int) -> List[Player]:
        room = self.get(roomID)
        if room is None:
            raise ValueError(f"Room with ID {roomID} not found")
        return room.players

    def update(self, room: Room) -> None:
        self.db_session.query(Room).filter(Room.roomID == room.roomID).update(
            {
                "roomName": room.roomName,
                "minPlayers": room.minPlayers,
                "maxPlayers": room.maxPlayers,
            }
        )
        self.db_session.commit()
        self.db_session.refresh(room)

    def delete_and_clean(self, roomID: int) -> None:
        if self.db_session.query(Room).filter(Room.roomID == roomID).one_or_none() is None:
            raise ValueError(f"Room with ID {roomID} not found")
        self.db_session.query(PlayerRoom).filter(PlayerRoom.roomID == roomID).delete()
        self.db_session.query(Room).filter(Room.roomID == roomID).delete()
        self.db_session.commit()

    def add_player_to_room(self, playerID: int, roomID: int) -> None:
        player_join_room = PlayerRoom(roomID=roomID, playerID=playerID)
        self.db_session.add(player_join_room)
        self.db_session.commit()

    def remove_player_from_room(self, playerID: int, roomID: int) -> None:
        player_in_room = self.db_session.query(PlayerRoom).filter(
            PlayerRoom.playerID == playerID, PlayerRoom.roomID == roomID
        )
        player_in_room.delete()
        self.db_session.commit()

    def is_owner(self, playerID: int, roomID: int) -> bool:
        room = self.db_session.query(Room).filter_by(hostID=playerID, roomID=roomID).one_or_none()
        return room is not None

    def is_player_in_room(self, playerID: int, roomID: int) -> bool:
        player_in_room = self.db_session.query(PlayerRoom).filter_by(playerID=playerID, roomID=roomID).one_or_none()
        return player_in_room is not None

    def is_game_started(self, roomID: int) -> bool:
        room = self.db_session.query(Room).filter_by(roomID=roomID).one_or_none()
        return room.game is not None

    def set_position(self, playerID: int, position: int, roomID: int) -> None:
        self.db_session.query(PlayerRoom).filter(PlayerRoom.playerID == playerID, PlayerRoom.roomID == roomID).update(
            {"position": position}
        )
        self.db_session.commit()

    def encrypt_password(self, password: str) -> str:
        if password is None:
            return None
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def get_first_turn(self, roomID: int) -> int:
        return (
            self.db_session.query(PlayerRoom)
            .filter(PlayerRoom.roomID == roomID, PlayerRoom.position == 1)
            .one()
            .playerID
        )

    def get_turn(self, roomID: int, posEnabled: int) -> int:
        return (
            self.db_session.query(PlayerRoom)
            .filter(PlayerRoom.roomID == roomID, PlayerRoom.position == posEnabled)
            .one()
            .playerID
        )


class WebSocketRepository(RoomRepositoryWS, SQLAlchemyRepository):
    async def setup_connection_room_list(self, websocket: WebSocket) -> None:
        """Establece la conexión con el websocket lista de salas
        y le envia el estado actual de la lista de salas

        Args:
            playerID (int): ID del jugador
            websocket (WebSocket): Conexión con el cliente
        """
        await ws_manager_room_list.connect(websocket)
        room_list = self.get_all_rooms()
        room_list_json = [room.model_dump() for room in room_list]
        await ws_manager_room_list.send_personal_message(MessageType.STATUS, room_list_json, websocket)
        await ws_manager_room_list.keep_listening(websocket)

    async def setup_connection_room(self, playerID: int, roomID: int, websocket: WebSocket) -> None:
        """Establece la conexión con el websocket de una sala
        y le envia el estado actual de la sala

        Args:
            playerID (int): ID del jugador
            roomID (int): ID de la sala
            websocket (WebSocket): Conexión con el cliente
        """
        await ws_manager_room.connect(playerID, roomID, websocket)
        room = self.get_public_info(roomID)
        if room is None:
            raise ValueError(f"Room with ID {roomID} not found")
        room_json = room.model_dump()
        await ws_manager_room.send_personal_message(MessageType.STATUS, room_json, websocket)
        await ws_manager_room.keep_listening(websocket)

    async def broadcast_status_room_list(self) -> None:
        """Envía la lista de salas (actualizada) a todos los clientes conectados a la lista de salas"""
        room_list = self.get_all_rooms()
        room_list_json = [room.model_dump() for room in room_list]
        await ws_manager_room_list.broadcast(MessageType.STATUS, room_list_json)

    async def broadcast_status_room(self, roomID: int) -> None:
        """Envía el estado de la sala (actualizado) a todos los clientes conectados a la sala

        Args:
            roomID (int): ID de la sala
        """
        room = self.get_public_info(roomID)
        if room is None:
            raise ValueError(f"Room with ID {roomID} not found")
        room_json = room.model_dump()
        await ws_manager_room.broadcast(MessageType.STATUS, room_json, roomID)

    async def broadcast_start_game(self, roomID: int, gameID: int) -> None:
        """Envía la señal de inicio de juego a todos los clientes conectados a la sala

        Args:
            roomID (int): ID de la sala
        """
        game_info = GameID(gameID=gameID)
        game_info_json = game_info.model_dump()
        await ws_manager_room.broadcast(MessageType.START_GAME, game_info_json, roomID)

    async def broadcast_room_cancellation(self, roomID: int) -> None:
        """Envía la señal de cancelación de sala a todos los clientes conectados a la sala

        Args:
            roomID (int): ID de la sala
        """
        room_json = "{}"
        players = self.get_players(roomID)
        for player in players:
            await ws_manager_room.send_personal_message_by_id(MessageType.END_ROOM, room_json, player.playerID, roomID)

    async def disconnect_player(self, playerID: int, roomID: int) -> None:
        """Remueve al jugador de la lista de conexiones activas

        Args:
            playerID (int): ID del jugador
            gameID (int): ID del juego
        """
        await ws_manager_room.disconnect_by_id_room(playerID, roomID)
