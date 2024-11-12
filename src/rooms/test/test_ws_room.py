import pytest
from fastapi.websockets import WebSocketDisconnect

from src.conftest import override_get_db
from src.games.infrastructure.models import Game as GameDB
from src.players.infrastructure.models import Player as PlayerDB
from src.rooms.infrastructure.models import PlayerRoom as PlayerRoom
from src.rooms.infrastructure.models import Room as RoomDB


def test_connect_to_room_websocket_user_not_exist(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            RoomDB(roomID=1, roomName="test room", maxPlayers=4, minPlayers=2, hostID=1),
            PlayerRoom(playerID=1, roomID=1),
            PlayerRoom(playerID=2, roomID=1),
        ]
    )
    db.commit()
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect("/rooms/3/2") as websocket:
            websocket.receive_json()
    assert e.value.code == 4004
    assert "no existe" in e.value.reason
    assert "jugador" in e.value.reason


def test_connect_to_room_websocket_room_not_exist(client, test_db):
    db = next(override_get_db())
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
        with client.websocket_connect("/rooms/1/2") as websocket:
            websocket.receive_json()
    assert e.value.code == 4004
    assert "no existe" in e.value.reason
    assert "sala" in e.value.reason


def test_connect_to_room_websocket_player_not_in_room(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoom(playerID=1, roomID=1),
        ]
    )
    db.commit()
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect("/rooms/2/1") as websocket:
            websocket.receive_json()
    assert e.value.code == 4003
    assert "jugador" in e.value.reason
    assert "no se encuentra" in e.value.reason
    assert "sala" in e.value.reason


def test_connect_to_room_websocket_player_in_room(client, test_db):
    db = next(override_get_db())
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
    with client.websocket_connect("/rooms/2/1") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == {
            "roomID": 1,
            "roomName": "test room",
            "minPlayers": 2,
            "maxPlayers": 4,
            "hostID": 1,
            "players": [
                {"playerID": 1, "username": "test user"},
                {"playerID": 2, "username": "test user 2"},
            ],
        }


def test_close_first_connection_if_player_open_second(client, test_db):
    db = next(override_get_db())
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
        with client.websocket_connect("/rooms/1/1") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "status"
            assert data["payload"] == {
                "roomID": 1,
                "roomName": "test room",
                "minPlayers": 2,
                "maxPlayers": 4,
                "hostID": 1,
                "players": [
                    {"playerID": 1, "username": "test user"},
                    {"playerID": 2, "username": "test user 2"},
                ],
            }

            with client.websocket_connect("/rooms/1/1") as websocket2:
                data = websocket2.receive_json()
                assert data["type"] == "status"
                assert data["payload"] == {
                    "roomID": 1,
                    "roomName": "test room",
                    "minPlayers": 2,
                    "maxPlayers": 4,
                    "hostID": 1,
                    "players": [
                        {"playerID": 1, "username": "test user"},
                        {"playerID": 2, "username": "test user 2"},
                    ],
                }

                websocket.receive_json()

    assert e.value.code == 4005
    assert e.value.reason == "Conexión abierta en otra pestaña"


def test_connect_to_room_ws_game_started(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoom(playerID=1, roomID=1),
            PlayerRoom(playerID=2, roomID=1),
            GameDB(roomID=1),
        ]
    )
    db.commit()
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect("/rooms/1/1") as websocket:
            websocket.receive_json()
    assert e.value.code == 4007
    assert "partida" in e.value.reason
    assert "comenzado" in e.value.reason
