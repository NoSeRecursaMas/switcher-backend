import json

from src.conftest import override_get_db
from src.games.infrastructure.models import FigureCard as FigureCardDB
from src.games.infrastructure.models import Game as GameDB
from src.games.infrastructure.models import MovementCard as MovementCardDB
from src.players.infrastructure.models import Player as PlayerDB
from src.rooms.infrastructure.models import PlayerRoom as PlayerRoomDB
from src.rooms.infrastructure.models import Room as RoomDB


def test_leave_game_player_not_exists(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoomDB(playerID=1, roomID=1, position=1),
            PlayerRoomDB(playerID=2, roomID=1, position=2),
            GameDB(roomID=1, board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)])),
        ]
    )

    db.commit()

    response = client.put("/games/1/leave", json={"playerID": 3})

    assert response.status_code == 404
    assert response.json() == {"detail": "El jugador no existe."}


def test_leave_game_game_not_exists(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoomDB(playerID=1, roomID=1, position=1),
            PlayerRoomDB(playerID=2, roomID=1, position=2),
            GameDB(
                roomID=1,
                board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
                posEnabledToPlay=2,
            ),
        ]
    )

    db.commit()

    response = client.put("/games/2/leave", json={"playerID": 1})

    assert response.status_code == 404
    assert response.json() == {"detail": "El juego no existe."}


def test_leave_game_player_not_in_game(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            PlayerDB(playerID=3, username="test user 3"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoomDB(playerID=1, roomID=1, position=1),
            PlayerRoomDB(playerID=2, roomID=1, position=2),
            GameDB(
                roomID=1,
                board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
                posEnabledToPlay=2,
            ),
        ]
    )

    db.commit()

    response = client.put("/games/1/leave", json={"playerID": 3})

    assert response.status_code == 403
    assert response.json() == {"detail": "El jugador no se encuentra en el juego."}


def test_leave_game(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            PlayerDB(playerID=3, username="test user 3"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoomDB(playerID=1, roomID=1, position=1),
            PlayerRoomDB(playerID=2, roomID=1, position=2),
            PlayerRoomDB(playerID=3, roomID=1, position=3),
            GameDB(
                roomID=1,
                board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
                posEnabledToPlay=1,
            ),
            FigureCardDB(gameID=1, type="fig01", isPlayable=False, playerID=1),
            FigureCardDB(gameID=1, type="fig02", isPlayable=False, playerID=1),
            FigureCardDB(gameID=1, type="fig02", isPlayable=False, playerID=1),
            MovementCardDB(gameID=1, type="mov01", playerID=1),
            MovementCardDB(gameID=1, type="mov02", playerID=1),
        ]
    )

    db.commit()

    response = client.put("/games/1/leave", json={"playerID": 1})

    assert response.status_code == 200
    assert response.json() is None

    game = db.query(GameDB).filter(GameDB.gameID == 1).first()
    assert game.posEnabledToPlay == 2

    player = db.query(PlayerRoomDB).filter(PlayerRoomDB.playerID == 1).first()
    assert not player.isActive

    player = db.query(PlayerRoomDB).filter(PlayerRoomDB.playerID == 2).first()
    assert player.isActive

    figure_cards = db.query(FigureCardDB).filter(FigureCardDB.gameID == 1, FigureCardDB.playerID == 1)
    assert figure_cards.count() == 0

    movement_cards = db.query(MovementCardDB).filter(MovementCardDB.gameID == 1, MovementCardDB.playerID == 1)
    assert movement_cards.count() == 0


def test_leave_game_with_2_players_removes_game(client, test_db):
    db = next(override_get_db())
    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoomDB(playerID=1, roomID=1, position=1),
            PlayerRoomDB(playerID=2, roomID=1, position=2),
            GameDB(
                roomID=1,
                board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
                posEnabledToPlay=1,
            ),
            FigureCardDB(gameID=1, type="fig01", isPlayable=False, playerID=1),
            FigureCardDB(gameID=1, type="fig02", isPlayable=False, playerID=1),
            FigureCardDB(gameID=1, type="fig02", isPlayable=False, playerID=1),
            MovementCardDB(gameID=1, type="mov01", playerID=1),
            MovementCardDB(gameID=1, type="mov02", playerID=1),
        ]
    )

    db.commit()

    response = client.put("/games/1/leave", json={"playerID": 1})

    assert response.status_code == 200
    assert response.json() is None

    assert db.query(GameDB).filter(GameDB.gameID == 1).count() == 0

    assert db.query(PlayerRoomDB).filter(PlayerRoomDB.roomID == 1).count() == 0

    assert db.query(FigureCardDB).filter(FigureCardDB.gameID == 1).count() == 0

    assert db.query(MovementCardDB).filter(MovementCardDB.gameID == 1).count() == 0

    assert db.query(RoomDB).filter(RoomDB.roomID == 1).count() == 0


def test_leave_game_with_2_players_send_ws_end_game(client, test_db):
    db = next(override_get_db())

    db.add_all(
        [
            PlayerDB(playerID=1, username="test user"),
            PlayerDB(playerID=2, username="test user 2"),
            RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
            PlayerRoomDB(playerID=1, roomID=1, position=1),
            PlayerRoomDB(playerID=2, roomID=1, position=2),
            GameDB(
                roomID=1,
                board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
                posEnabledToPlay=1,
            ),
            FigureCardDB(gameID=1, type="fig01", isPlayable=False, playerID=1),
            FigureCardDB(gameID=1, type="fig02", isPlayable=False, playerID=1),
            FigureCardDB(gameID=1, type="fig02", isPlayable=False, playerID=1),
            MovementCardDB(gameID=1, type="mov01", playerID=1),
            MovementCardDB(gameID=1, type="mov02", playerID=1),
        ]
    )

    db.commit()

    with client.websocket_connect("/games/2/1") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        payload = data["payload"]
        assert payload["posEnabledToPlay"] == 1
        assert len(payload["players"]) == 2

        response = client.put("/games/1/leave", json={"playerID": 1})

        assert response.status_code == 200
        assert response.json() is None

        message = websocket.receive_json()

        assert message["type"] == "end"
        assert message["payload"] == {"winnerID": 2, "username": "test user 2"}
