import bcrypt

from src.conftest import override_get_db
from src.games.infrastructure.models import Game as GameDB
from src.players.infrastructure.models import Player as PlayerDB
from src.rooms.infrastructure.models import PlayerRoom as PlayerRoomDB
from src.rooms.infrastructure.models import Room as RoomDB


def test_join_room(client, test_db):
    db = next(override_get_db())
    player1 = PlayerDB(username="player1")
    db.add(player1)
    db.commit()

    room = RoomDB(roomName="testjoinroom", minPlayers=2, maxPlayers=4, hostID=player1.playerID)
    db.add(room)
    db.commit()

    response = client.put(f"/rooms/{room.roomID}/join", json={"playerID": player1.playerID})
    assert response.status_code == 200


def test_join_room_not_exists(client, test_db):
    db = next(override_get_db())
    player1 = PlayerDB(username="player1")
    db.add(player1)
    db.commit()

    response = client.put(f"/rooms/1/join", json={"playerID": player1.playerID})

    assert response.status_code == 404


def test_join_room_full(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 6)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[2].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[3].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()

    response = client.put(f"/rooms/{room.roomID}/join", json={"playerID": players[4].playerID})

    assert response.status_code == 403
    assert response.json() == {"detail": "La sala está llena."}


def test_join_room_send_update_ws_room_list(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 6)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[2].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()

    with client.websocket_connect(f"/rooms/{players[3].playerID}") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == [
            {
                "roomID": 1,
                "roomName": "test_room1",
                "maxPlayers": 4,
                "actualPlayers": 3,
                "started": False,
                "private": False,
                "playersID": [1, 2, 3],
            },
        ]

        response = client.put(f"/rooms/{room.roomID}/join", json={"playerID": players[3].playerID})
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == [
            {
                "roomID": 1,
                "roomName": "test_room1",
                "maxPlayers": 4,
                "actualPlayers": 4,
                "started": False,
                "private": False,
                "playersID": [1, 2, 3, 4],
            },
        ]
        assert response.status_code == 200


def test_join_room_send_update_ws_room(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 6)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[2].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()

    with client.websocket_connect(f"/rooms/{players[1].playerID}/1") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == {
            "roomID": 1,
            "roomName": "test_room1",
            "minPlayers": 2,
            "maxPlayers": 4,
            "hostID": 1,
            "players": [
                {"playerID": 1, "username": "player1"},
                {"playerID": 2, "username": "player2"},
                {"playerID": 3, "username": "player3"},
            ],
        }

        response = client.put(f"/rooms/{room.roomID}/join", json={"playerID": players[3].playerID})
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == {
            "roomID": 1,
            "roomName": "test_room1",
            "minPlayers": 2,
            "maxPlayers": 4,
            "hostID": 1,
            "players": [
                {"playerID": 1, "username": "player1"},
                {"playerID": 2, "username": "player2"},
                {"playerID": 3, "username": "player3"},
                {"playerID": 4, "username": "player4"},
            ],
        }
        assert response.status_code == 200


def test_join_room_game_started(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
    ]
    db.add_all(players_room_relations)
    db.commit()

    game = GameDB(roomID=room.roomID, board={}, lastMovements={}, prohibitedColor=None)
    db.add(game)
    db.commit()

    player_id = {"playerID": players[1].playerID}

    response_leave = client.put(f"/rooms/{room.roomID}/join", json=player_id)

    assert response_leave.status_code == 403
    assert response_leave.json() == {"detail": "La partida ya ha comenzado."}


def test_join_room_password(client, test_db):
    db = next(override_get_db())
    player = PlayerDB(username="player")
    db.add(player)
    db.commit()

    hashed_password = bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode()
    room = RoomDB(roomName="test_room", minPlayers=2, maxPlayers=4, hostID=player.playerID, password=hashed_password)
    db.add(room)
    db.commit()

    response = client.put(f"/rooms/{room.roomID}/join", json={"playerID": player.playerID, "password": "1234"})

    assert response.status_code == 200


def test_join_room_password_incorrect(client, test_db):
    db = next(override_get_db())
    player = PlayerDB(username="player")
    db.add(player)
    db.commit()

    hashed_password = bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode()
    room = RoomDB(roomName="test_room", minPlayers=2, maxPlayers=4, hostID=player.playerID, password=hashed_password)
    db.add(room)
    db.commit()

    response = client.put(f"/rooms/{room.roomID}/join", json={"playerID": player.playerID, "password": "12345"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Contraseña incorrecta."}


def test_join_room_without_password(client, test_db):
    db = next(override_get_db())
    player = PlayerDB(username="player")
    db.add(player)
    db.commit()

    room = RoomDB(roomName="test_room", minPlayers=2, maxPlayers=4, hostID=player.playerID, password="")
    db.add(room)
    db.commit()

    response = client.put(f"/rooms/{room.roomID}/join", json={"playerID": player.playerID, "password": "1234"})

    assert response.status_code == 403
    assert response.json() == {"detail": "La sala no tiene contraseña."}
