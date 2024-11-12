import json

import pytest
from fastapi.websockets import WebSocketDisconnect, WebSocket

from src.conftest import override_get_db
from src.games.infrastructure.models import Game as GameDB
from src.players.infrastructure.models import Player as PlayerDB
from src.rooms.infrastructure.models import PlayerRoom as PlayerRoom
from src.rooms.infrastructure.models import Room as RoomDB
from src.games.infrastructure.websocket import ConnectionManagerGame

def test_connect_to_game_websocket_user_not_exist(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            RoomDB(roomID=1, roomName="test room", maxPlayers=4, minPlayers=2, hostID=1),
            PlayerRoom(playerID=1, roomID=1),
            PlayerRoom(playerID=2, roomID=1),
            GameDB(roomID=1),
        ]
    )
    db.commit()
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect("/games/3/1") as websocket:
            websocket.receive_json()
    assert e.value.code == 4004
    assert "no existe" in e.value.reason
    assert "jugador" in e.value.reason


def test_connect_to_game_websocket_game_not_exist(client, test_db):
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
        with client.websocket_connect("/games/1/2") as websocket:
            websocket.receive_json()
    assert e.value.code == 4004
    assert "no existe" in e.value.reason
    assert "juego" in e.value.reason


def test_connect_to_game_websocket_game_not_started(client, test_db):
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
        with client.websocket_connect("/games/1/1") as websocket:
            websocket.receive_json()
    assert e.value.code == 4004
    assert "no existe" in e.value.reason
    assert "juego" in e.value.reason


def test_connect_to_game_websocket_player_not_in_game(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            PlayerDB(playerID=3, username="test user 3"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoom(playerID=1, roomID=1),
            PlayerRoom(playerID=2, roomID=1),
            GameDB(roomID=1, board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)])),
        ]
    )
    db.commit()
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect("/games/3/1") as websocket:
            websocket.receive_json()
    assert e.value.code == 4003
    assert "jugador" in e.value.reason
    assert "no se encuentra" in e.value.reason
    assert "juego" in e.value.reason


def test_connect_to_game_websocket_player_in_game(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            PlayerDB(playerID=3, username="test user 3"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoom(playerID=1, roomID=1),
            PlayerRoom(playerID=2, roomID=1),
            PlayerRoom(playerID=3, roomID=1),
            GameDB(roomID=1, board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)])),
        ]
    )
    db.commit()
    with client.websocket_connect("/games/3/1") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        payload = data["payload"]
        assert payload["gameID"] == 1
        assert len(payload["board"]) == 36
        assert "position" in payload["players"][0]
        assert "username" in payload["players"][0]
        assert "playerID" in payload["players"][0]
        assert payload["players"][0]["isActive"]
        assert "sizeDeckFigure" in payload["players"][0]
        assert "cardsFigure" in payload["players"][0]
        assert "cardsMovement" in payload["players"][0]


def test_close_connection_if_player_open_second(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoom(playerID=1, roomID=1),
            PlayerRoom(playerID=2, roomID=1),
            GameDB(
                roomID=1,
                board=json.dumps(
                    [
                        {"posX": 0, "posY": 0, "color": "G", "isPartial": False},
                        {"posX": 0, "posY": 1, "color": "Y", "isPartial": False},
                        {"posX": 0, "posY": 2, "color": "G", "isPartial": False},
                        {"posX": 0, "posY": 3, "color": "G", "isPartial": False},
                        {"posX": 0, "posY": 4, "color": "B", "isPartial": False},
                        {"posX": 0, "posY": 5, "color": "Y", "isPartial": False},
                        {"posX": 1, "posY": 0, "color": "G", "isPartial": False},
                        {"posX": 1, "posY": 1, "color": "B", "isPartial": False},
                        {"posX": 1, "posY": 2, "color": "B", "isPartial": False},
                        {"posX": 1, "posY": 3, "color": "Y", "isPartial": False},
                        {"posX": 1, "posY": 4, "color": "B", "isPartial": False},
                        {"posX": 1, "posY": 5, "color": "Y", "isPartial": False},
                        {"posX": 2, "posY": 0, "color": "Y", "isPartial": False},
                        {"posX": 2, "posY": 1, "color": "Y", "isPartial": False},
                        {"posX": 2, "posY": 2, "color": "R", "isPartial": False},
                        {"posX": 2, "posY": 3, "color": "R", "isPartial": False},
                        {"posX": 2, "posY": 4, "color": "B", "isPartial": False},
                        {"posX": 2, "posY": 5, "color": "G", "isPartial": False},
                        {"posX": 3, "posY": 0, "color": "R", "isPartial": False},
                        {"posX": 3, "posY": 1, "color": "R", "isPartial": False},
                        {"posX": 3, "posY": 2, "color": "B", "isPartial": False},
                        {"posX": 3, "posY": 3, "color": "G", "isPartial": False},
                        {"posX": 3, "posY": 4, "color": "R", "isPartial": False},
                        {"posX": 3, "posY": 5, "color": "Y", "isPartial": False},
                        {"posX": 4, "posY": 0, "color": "Y", "isPartial": False},
                        {"posX": 4, "posY": 1, "color": "G", "isPartial": False},
                        {"posX": 4, "posY": 2, "color": "Y", "isPartial": False},
                        {"posX": 4, "posY": 3, "color": "R", "isPartial": False},
                        {"posX": 4, "posY": 4, "color": "R", "isPartial": False},
                        {"posX": 4, "posY": 5, "color": "G", "isPartial": False},
                        {"posX": 5, "posY": 0, "color": "Y", "isPartial": False},
                        {"posX": 5, "posY": 1, "color": "G", "isPartial": False},
                        {"posX": 5, "posY": 2, "color": "B", "isPartial": False},
                        {"posX": 5, "posY": 3, "color": "B", "isPartial": False},
                        {"posX": 5, "posY": 4, "color": "R", "isPartial": False},
                        {"posX": 5, "posY": 5, "color": "G", "isPartial": False},
                    ]
                ),
            ),
        ]
    )
    db.commit()
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect("/games/1/1") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "status"
            assert data["payload"]["players"][0]["isActive"]
            with client.websocket_connect("/games/1/1") as websocket2:
                data = websocket2.receive_json()
                assert data["type"] == "status"
                assert data["payload"]["players"][0]["isActive"]
                websocket.receive_json()
    assert e.value.code == 4005
    assert e.value.reason == "Conexión abierta en otra pestaña"

def test_send_personal_message(client, test_db):
    db = next(override_get_db())
    db.add_all([
        PlayerDB(playerID=1, username="test user"),
        RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
        PlayerRoom(playerID=1, roomID=1),
        GameDB(roomID=1, board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)])),
    ])
    db.commit()
    with client.websocket_connect("/games/1/1") as websocket:
        websocket.receive_json() 
        message = {"type": "msg", "payload": "Hello Player"}
        websocket.send_json(message)
        data = websocket.receive_json()
        assert data == message

def test_clean_up_connections(client, test_db):
    db = next(override_get_db())
    db.add_all([
        PlayerDB(playerID=1, username="test user"),
        RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
        PlayerRoom(playerID=1, roomID=1),
        GameDB(roomID=1, board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)])),
    ])
    db.commit()
    with client.websocket_connect("/games/1/1") as websocket:
        websocket.receive_json()  
        manager = ConnectionManagerGame()
        manager.clean_up()
        assert not manager.active_connections

def test_broadcast_message(client, test_db):
    db = next(override_get_db())
    db.add_all([
        PlayerDB(playerID=1, username="test user 1"),
        PlayerDB(playerID=2, username="test user 2"),
        RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
        PlayerRoom(playerID=1, roomID=1),
        PlayerRoom(playerID=2, roomID=1),
        GameDB(roomID=1, board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)])),
    ])
    db.commit()


    with client.websocket_connect("/games/1/1") as websocket1, \
         client.websocket_connect("/games/2/1") as websocket2:
        
        websocket1.receive_json()
        websocket2.receive_json()
    
        broadcast_message = {"type": "msg", "payload": "Game broadcast message"}

        websocket1.send_json(broadcast_message)
        websocket2.send_json(broadcast_message)

        data1 = websocket1.receive_json()
        data2 = websocket2.receive_json()
        assert data1 == broadcast_message
        assert data2 == broadcast_message