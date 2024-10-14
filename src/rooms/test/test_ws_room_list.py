import pytest
from fastapi.websockets import WebSocketDisconnect
from src.rooms.infrastructure.models import Room as RoomDB
from src.rooms.infrastructure.models import PlayerRoom as PlayerRoomDB
from src.players.infrastructure.models import Player as PlayerDB
from src.conftest import override_get_db


def test_connect_to_room_list_websocket_user_not_exist(client, test_db):
    db = next(override_get_db())
    db.add_all([
        PlayerDB(playerID=1, username="test user"),
        PlayerDB(playerID=2, username="test user 2"),
    ])
    db.commit()
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect("/rooms/3") as websocket:
            websocket.receive_json()
    assert e.value.code == 4004
    assert "no existe" in e.value.reason
    assert "jugador" in e.value.reason


def test_connect_to_room_list_websocket_player_exist_and_no_rooms(client, test_db):
    db = next(override_get_db())
    db.add_all([
        PlayerDB(playerID=1, username="test user"),
        PlayerDB(playerID=2, username="test user 2"),
    ])
    db.commit()

    with client.websocket_connect("/rooms/1") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == []

def test_connect_to_room_list_websocket_player_exist_and_has_rooms(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 6)]
    db.add_all(players)

    rooms = [RoomDB(roomName=f"test_room{i}", minPlayers=2, maxPlayers=4, hostID=players[i-1].playerID) for i in range(1, 3)]
    db.add_all(rooms)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=rooms[0].roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=rooms[1].roomID),
        PlayerRoomDB(playerID=players[2].playerID, roomID=rooms[0].roomID),
    ]
    db.add_all(players_room_relations)
    db.commit()

    with client.websocket_connect("/rooms/5") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == [
            {
                "roomID": 1,
                "roomName": "test_room1",
                "maxPlayers": 4,
                "actualPlayers": 2,
                "started": False,
                "private": False,
            },
            {
                "roomID": 2,
                "roomName": "test_room2",
                "maxPlayers": 4,
                "actualPlayers": 1,
                "started": False,
                "private": False,
            },
        ]
  
def test_can_connect_2_times(client, test_db):
    db = next(override_get_db())
    db.add_all([
        PlayerDB(playerID=1, username="test user"),
        PlayerDB(playerID=2, username="test user 2"),
        RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
        PlayerRoomDB(playerID=1, roomID=1),
        PlayerRoomDB(playerID=2, roomID=1),
    ])
    db.commit()

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


def test_get_all_rooms_via_websocket(client, test_db):
  
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 10)]
    db.add_all(players)

    rooms = [RoomDB(roomName=f"test_room{i}", minPlayers=2, maxPlayers=4, hostID=players[i-1].playerID) for i in range(1, 5)]
    db.add_all(rooms)    
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=rooms[0].roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=rooms[1].roomID),
        PlayerRoomDB(playerID=players[2].playerID, roomID=rooms[2].roomID),
        PlayerRoomDB(playerID=players[3].playerID, roomID=rooms[3].roomID),
        PlayerRoomDB(playerID=players[4].playerID, roomID=rooms[1].roomID),
        PlayerRoomDB(playerID=players[5].playerID, roomID=rooms[2].roomID),
        PlayerRoomDB(playerID=players[6].playerID, roomID=rooms[3].roomID),
        PlayerRoomDB(playerID=players[7].playerID, roomID=rooms[0].roomID),
        PlayerRoomDB(playerID=players[8].playerID, roomID=rooms[1].roomID),
    ]
    db.add_all(players_room_relations)
    db.commit()

    with client.websocket_connect(f"/rooms/{players[0].playerID}") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == [
            {
                "roomID": 1,
                "roomName": "test_room1",
                "maxPlayers": 4,
                "actualPlayers": 2,
                "started": False,
                "private": False,
            },
            {
                "roomID": 2,
                "roomName": "test_room2",
                "maxPlayers": 4,
                "actualPlayers": 3,
                "started": False,
                "private": False,
            },
            {
                "roomID": 3,
                "roomName": "test_room3",
                "maxPlayers": 4,
                "actualPlayers": 2,
                "started": False,
                "private": False,
            },
            {
                "roomID": 4,
                "roomName": "test_room4",
                "maxPlayers": 4,
                "actualPlayers": 2,
                "started": False,
                "private": False,
            },

        ]

def test_get_empty_room(client,test_db):
    db = next(override_get_db())
    player1 = PlayerDB(username="player1")
    db.add(player1)
    db.commit()

    with client.websocket_connect(f"/rooms/{player1.playerID}") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == []