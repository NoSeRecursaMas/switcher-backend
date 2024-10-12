import pytest
from fastapi.websockets import WebSocketDisconnect

from src.conftest import TestingSessionLocal
from src.players.infrastructure.models import Player as PlayerDB
from src.rooms.infrastructure.models import PlayerRoom
from src.rooms.infrastructure.models import Room as RoomDB


def test_connect_to_room_list_websocket_user_not_exist(client, test_db):
    db = TestingSessionLocal()
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
        ]
    )
    db.commit()
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect("/rooms/3") as websocket:
            websocket.receive_json()
    assert e.value.code == 4004
    assert "no existe" in e.value.reason
    assert "jugador" in e.value.reason


def test_connect_to_room_list_websocket_player_exist_and_no_rooms(client, test_db):
    db = TestingSessionLocal()
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
        ]
    )
    db.commit()

    with client.websocket_connect("/rooms/1") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == []


def test_connect_to_room_list_websocket_player_exist_and_has_rooms(client, test_db):
    db = TestingSessionLocal()
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            PlayerDB(playerID=3, username="test user 3"),
            PlayerDB(playerID=4, username="test user 4"),
            PlayerDB(playerID=5, username="test user 5"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            RoomDB(roomID=2, roomName="test room 2", minPlayers=2, maxPlayers=4, hostID=2),
            PlayerRoom(playerID=1, roomID=1),
            PlayerRoom(playerID=1, roomID=2),
            PlayerRoom(playerID=2, roomID=1),
        ]
    )

    db.commit()

    with client.websocket_connect("/rooms/5") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == [
            {
                "roomID": 1,
                "roomName": "test room",
                "maxPlayers": 4,
                "actualPlayers": 2,
                "started": False,
                "private": False,
            },
            {
                "roomID": 2,
                "roomName": "test room 2",
                "maxPlayers": 4,
                "actualPlayers": 1,
                "started": False,
                "private": False,
            },
        ]


def test_close_first_connection_if_player_open_second(client, test_db):
    db = TestingSessionLocal()
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoom(playerID=1, roomID=1),
            PlayerRoom(playerID=2, roomID=1),
        ]
    )
    db.commit()

    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect("/rooms/1") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "status"
            assert data["payload"] == [
                {
                    "roomID": 1,
                    "roomName": "test room",
                    "maxPlayers": 4,
                    "actualPlayers": 2,
                    "started": False,
                    "private": False,
                },
            ]

            with client.websocket_connect("/rooms/1") as websocket2:
                data = websocket2.receive_json()
                assert data["type"] == "status"
                assert data["payload"] == [
                    {
                        "roomID": 1,
                        "roomName": "test room",
                        "maxPlayers": 4,
                        "actualPlayers": 2,
                        "started": False,
                        "private": False,
                    },
                ]

                websocket.receive_json()

    assert e.value.code == 1000
    assert e.value.reason == "Conexión abierta en otra pestaña"
