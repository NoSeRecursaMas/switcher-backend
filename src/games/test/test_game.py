import json

import pytest

from src.conftest import override_get_db
from src.games.infrastructure.models import FigureCard as FigureCardDB
from src.games.infrastructure.models import Game as GameDB
from src.games.infrastructure.models import MovementCard as MovementCardDB
from src.players.infrastructure.models import Player as PlayerDB
from src.rooms.infrastructure.models import PlayerRoom as PlayerRoomDB
from src.rooms.infrastructure.models import Room as RoomDB


def create_game_generalization_two_players(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()

    return db, players, room


def test_create_game(client, test_db):
    db, players, room = create_game_generalization_two_players(client, test_db)

    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})

    assert response.status_code == 201
    assert response.json() == {"gameID": 1}


def test_create_game_prohibited_color(client, test_db):
    db, players, room = create_game_generalization_two_players(client, test_db)

    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})

    assert response.status_code == 201
    assert db.get(GameDB, 1).prohibitedColor == None
    assert response.json() == {"gameID": 1}


def test_create_game_cards(client, test_db):
    db, players, room = create_game_generalization_two_players(client, test_db)

    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})

    figure_cards = db.query(FigureCardDB).filter(FigureCardDB.gameID == 1).count()
    movement_cards = db.query(MovementCardDB).filter(MovementCardDB.gameID == 1).count()

    assert figure_cards == 50
    assert movement_cards == 48


def test_create_game_not_minimum_players(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 2)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()

    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})
    assert response.status_code == 403
    assert response.json() == {"detail": "No hay suficientes jugadores para iniciar la partida."}


def test_player_is_not_owner(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[1].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()

    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})
    assert response.status_code == 403
    assert response.json() == {"detail": "Solo el propietario puede iniciar la partida."}


def test_game_room_not_exists(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[1].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()

    response = client.post(f"/games/2", json={"playerID": players[0].playerID})
    assert response.status_code == 404
    assert response.json() == {"detail": "La sala no existe."}


def test_player_exists(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()

    response = client.post(f"/games/{room.roomID}", json={"playerID": 3})
    assert response.status_code == 404
    assert response.json() == {"detail": "El jugador no existe."}


def test_create_game_send_update_room_list_ws(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
    ]


def test_create_game_send_update_room_list_ws_2(client, test_db):
    db, players, room = create_game_generalization_two_players(client, test_db)

    with client.websocket_connect(f"/rooms/{players[1].playerID}") as websocket:
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
                "playersID": [1, 2],
            },
        ]

        response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})

        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == [
            {
                "roomID": 1,
                "roomName": "test_room1",
                "maxPlayers": 4,
                "actualPlayers": 2,
                "started": True,
                "private": False,
                "playersID": [1, 2],
            },
        ]

        response.status_code == 201
        response.json() == {"gameID": 1}


def test_skip_turn(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID, position=1),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID, position=2),
    ]

    db.add_all(players_room_relations)
    db.commit()
    game = GameDB(
        gameID=1,
        roomID=room.roomID,
        board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
        posEnabledToPlay=1,
    )

    db.add(game)
    db.commit()

    assert game.posEnabledToPlay == 1

    response = client.put(f"/games/{game.gameID}/turn", json={"playerID": players[0].playerID})
    assert response.status_code == 200
    db.refresh(game)
    assert game.posEnabledToPlay == 2


def test_skip_turn_ws(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID, position=1),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID, position=2),
    ]

    db.add_all(players_room_relations)
    db.commit()
    game = GameDB(
        gameID=1,
        roomID=room.roomID,
        board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
        posEnabledToPlay=1,
    )

    db.add(game)
    db.commit()

    with client.websocket_connect(f"/games/{players[0].playerID}/1") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        payload = data["payload"]
        assert payload["posEnabledToPlay"] == 1

        response = client.put(f"/games/{game.gameID}/turn", json={"playerID": players[0].playerID})
        data = websocket.receive_json()
        assert data["type"] == "msg"
        data = websocket.receive_json()
        assert data["type"] == "status"
        payload = data["payload"]
        assert payload["posEnabledToPlay"] == 2

        response.status_code == 200


def test_skip_turn_not_player_in_game(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 4)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()
    game = GameDB(
        gameID=1,
        roomID=room.roomID,
        board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
        posEnabledToPlay=1,
    )

    db.add(game)
    db.commit()

    assert game.posEnabledToPlay == 1

    response = client.put(f"/games/{game.gameID}/turn", json={"playerID": 3})
    assert response.status_code == 403
    assert response.json() == {"detail": "El jugador no se encuentra en el juego."}


def test_skip_turn_not_player_turn(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID, position=1),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID, position=2),
    ]

    db.add_all(players_room_relations)
    db.commit()
    game = GameDB(
        gameID=1,
        roomID=room.roomID,
        board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
        posEnabledToPlay=2,
    )

    db.add(game)
    db.commit()

    assert game.posEnabledToPlay == 2

    response = client.put(f"/games/{game.gameID}/turn", json={"playerID": players[0].playerID})
    assert response.status_code == 403
    assert response.json() == {"detail": "No es el turno del jugador."}


def test_skip_turn_not_game_exists(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID, position=1),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID, position=2),
    ]

    db.add_all(players_room_relations)
    db.commit()

    game = GameDB(
        gameID=1,
        roomID=room.roomID,
        board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
        posEnabledToPlay=2,
    )

    db.add(game)
    db.commit()

    assert game.posEnabledToPlay == 2

    response = client.put(f"/games/2/turn", json={"playerID": players[0].playerID})
    assert response.status_code == 404
    assert response.json() == {"detail": "El juego no existe."}


def test_skip_turn_not_player_exists(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID, position=1),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID, position=2),
    ]

    db.add_all(players_room_relations)
    db.commit()
    game = GameDB(
        gameID=1,
        roomID=room.roomID,
        board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
        posEnabledToPlay=2,
    )

    db.add(game)
    db.commit()

    assert game.posEnabledToPlay == 2

    response = client.put(f"/games/{game.gameID}/turn", json={"playerID": 3})
    assert response.status_code == 404
    assert response.json() == {"detail": "El jugador no existe."}


def test_skip_turn_not_game_started(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID, position=1),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID, position=2),
    ]

    db.add_all(players_room_relations)
    db.commit()
    game = GameDB(
        gameID=1,
        roomID=room.roomID,
        board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
        posEnabledToPlay=2,
    )

    db.add(game)
    db.commit()

    assert game.posEnabledToPlay == 2

    response = client.put(f"/games/2/turn", json={"playerID": players[0].playerID})
    assert response.status_code == 404
    assert response.json() == {"detail": "El juego no existe."}


def test_skip_turn_full_round(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID=players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID, position=1),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID, position=2),
    ]

    db.add_all(players_room_relations)
    db.commit()
    game = GameDB(
        gameID=1,
        roomID=room.roomID,
        board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
        posEnabledToPlay=1,
    )

    db.add(game)
    db.commit()

    assert game.posEnabledToPlay == 1

    response = client.put(f"/games/{game.gameID}/turn", json={"playerID": players[0].playerID})
    assert response.status_code == 200
    db.refresh(game)
    assert game.posEnabledToPlay == 2
    assert response.status_code == 200

    response = client.put(f"/games/{game.gameID}/turn", json={"playerID": players[1].playerID})
    assert response.status_code == 200
    db.refresh(game)
    assert game.posEnabledToPlay == 1
    assert response.status_code == 200

    response = client.put(f"/games/{game.gameID}/turn", json={"playerID": players[0].playerID})
    assert response.status_code == 200
    db.refresh(game)
    assert game.posEnabledToPlay == 2
    assert response.status_code == 200

    response = client.put(f"/games/{game.gameID}/turn", json={"playerID": players[1].playerID})
    assert response.status_code == 200
    db.refresh(game)
    assert game.posEnabledToPlay == 1
    assert response.status_code == 200


def test_skip_turn_give_cards_figure(client, test_db):
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

    figure_cards = [
        FigureCardDB(gameID=1, type="fig01", isPlayable=False, playerID=1),
        FigureCardDB(gameID=1, type="fig02", isPlayable=False, playerID=1),
        FigureCardDB(gameID=1, type="fig03", isPlayable=False, playerID=1),
    ]

    db.add_all(figure_cards)
    db.commit()

    response = client.put("/games/1/turn", json={"playerID": 1})
    assert response.status_code == 200

    db.refresh(figure_cards[0])
    db.refresh(figure_cards[1])
    db.refresh(figure_cards[2])
    assert figure_cards[0].isPlayable
    assert figure_cards[1].isPlayable
    assert figure_cards[2].isPlayable


def test_skip_turn_not_give_cards_figure_because_player_has_blocked_cards(client, test_db):
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

    figure_cards = [
        FigureCardDB(gameID=1, type="fig01", isPlayable=True, isBlocked=True, playerID=1),
        FigureCardDB(gameID=1, type="fig01", isPlayable=False, playerID=1),
        FigureCardDB(gameID=1, type="fig02", isPlayable=False, playerID=1),
        FigureCardDB(gameID=1, type="fig03", isPlayable=False, playerID=1),
    ]

    db.add_all(figure_cards)
    db.commit()

    response = client.put("/games/1/turn", json={"playerID": 1})
    assert response.status_code == 200

    db.refresh(figure_cards[0])
    db.refresh(figure_cards[1])
    db.refresh(figure_cards[2])
    db.refresh(figure_cards[3])
    assert figure_cards[0].isPlayable
    assert not figure_cards[1].isPlayable
    assert not figure_cards[2].isPlayable
    assert not figure_cards[3].isPlayable


def test_skip_can_give_less_than_3_cards_figure(client, test_db):
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

    figure_cards = [
        FigureCardDB(gameID=1, type="fig01", isPlayable=False, playerID=1),
        FigureCardDB(gameID=1, type="fig02", isPlayable=False, playerID=1),
    ]

    db.add_all(figure_cards)
    db.commit()

    response = client.put("/games/1/turn", json={"playerID": 1})
    assert response.status_code == 200

    db.refresh(figure_cards[0])
    db.refresh(figure_cards[1])
    assert figure_cards[0].isPlayable
    assert figure_cards[1].isPlayable


def test_skip_turn_give_cards_movement(client, test_db):
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

    movement_cards = [
        MovementCardDB(gameID=1, type="mov01", isDiscarded=False),
        MovementCardDB(gameID=1, type="mov02", isDiscarded=False),
        MovementCardDB(gameID=1, type="mov03", isDiscarded=False),
    ]

    db.add_all(movement_cards)
    db.commit()

    response = client.put("/games/1/turn", json={"playerID": 1})
    assert response.status_code == 200

    db.refresh(movement_cards[0])
    db.refresh(movement_cards[1])
    db.refresh(movement_cards[2])
    assert movement_cards[0].playerID == 1
    assert movement_cards[1].playerID == 1
    assert movement_cards[2].playerID == 1


def test_skip_turn_give_cards_movement_rebuild_deck(client, test_db):
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

    movement_cards = [
        MovementCardDB(gameID=1, type="mov01", isDiscarded=True),
        MovementCardDB(gameID=1, type="mov02", isDiscarded=True),
        MovementCardDB(gameID=1, type="mov03", isDiscarded=True),
        MovementCardDB(gameID=1, type="mov04", isDiscarded=True),
        MovementCardDB(gameID=1, type="mov05", isDiscarded=True),
    ]

    db.add_all(movement_cards)
    db.commit()

    response = client.put("/games/1/turn", json={"playerID": 1})
    assert response.status_code == 200

    db.refresh(movement_cards[0])
    db.refresh(movement_cards[1])
    db.refresh(movement_cards[2])
    db.refresh(movement_cards[3])
    db.refresh(movement_cards[4])
    assert not movement_cards[0].isDiscarded
    assert not movement_cards[1].isDiscarded
    assert not movement_cards[2].isDiscarded
    assert not movement_cards[3].isDiscarded
    assert not movement_cards[4].isDiscarded

    cards_player = db.query(MovementCardDB).filter(MovementCardDB.gameID == 1, MovementCardDB.playerID == 1).count()
    assert cards_player == 3


# - Testear que no se crean más de 2 cartas de figuras iguales por cada tipo


def test_create_game_figure_cards_unique(client, test_db):
    db, players, room = create_game_generalization_two_players(client, test_db)

    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})

    figure_cards = db.query(FigureCardDB).filter(FigureCardDB.gameID == 1).all()
    figure_cards_count_by_type = {}
    for card in figure_cards:
        if card.type not in figure_cards_count_by_type:
            figure_cards_count_by_type[card.type] = 0
        figure_cards_count_by_type[card.type] += 1

    for count in figure_cards_count_by_type.values():
        assert count == 2


# - Testear que no se crean más de 7 cartas de movimiento iguales por cada tipo
def test_create_game_movement_cards_unique(client, test_db):
    db, players, room = create_game_generalization_two_players(client, test_db)

    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})

    movement_cards = db.query(MovementCardDB).filter(MovementCardDB.gameID == 1).all()
    movement_cards_count_by_type = {}
    for card in movement_cards:
        if card.type not in movement_cards_count_by_type:
            movement_cards_count_by_type[card.type] = 0
        movement_cards_count_by_type[card.type] += 1

    for count in movement_cards_count_by_type.values():
        assert count <= 7


# - Testear que se crea un tablero con 9 celdas de cada color
def test_create_game_board(client, test_db):
    db, players, room = create_game_generalization_two_players(client, test_db)

    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})

    game = db.get(GameDB, 1)
    board = json.loads(game.board)

    color_count = {}
    for cell in board:
        if cell["color"] not in color_count:
            color_count[cell["color"]] = 0
        color_count[cell["color"]] += 1

    for count in color_count.values():
        assert count == 9


# - Testear que se asigna el turno de los jugadores correctamente
def test_create_game_turn_order(client, test_db):
    db, players, room = create_game_generalization_two_players(client, test_db)

    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})

    game = db.get(GameDB, 1)
    players = db.query(PlayerRoomDB).filter(PlayerRoomDB.roomID == room.roomID).all()

    assert game.posEnabledToPlay == 1
    assert len(players) == 2
    assert players[0].position == players[0].position


# - Testear que se le asigna la cantidad correcta de cartas figura visibles y no visibles a cada jugador
def test_create_game_player_cards(client, test_db):
    db, players, room = create_game_generalization_two_players(client, test_db)
    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})

    figure_cards = db.query(FigureCardDB).filter(FigureCardDB.gameID == 1).all()
    movement_cards = db.query(MovementCardDB).filter(MovementCardDB.gameID == 1).all()

    figure_cards_by_player = {}
    playable_figure_cards_by_player = {}
    movements_cards_by_player = {}

    for card in figure_cards:
        if card.playerID not in figure_cards_by_player:
            figure_cards_by_player[card.playerID] = 0
            playable_figure_cards_by_player[card.playerID] = 0
        figure_cards_by_player[card.playerID] += 1
        if card.isPlayable:
            playable_figure_cards_by_player[card.playerID] += 1

    for card in movement_cards:
        if card.playerID not in movements_cards_by_player:
            movements_cards_by_player[card.playerID] = 0
        movements_cards_by_player[card.playerID] += 1

    for playerID in figure_cards_by_player.keys():
        assert playable_figure_cards_by_player[playerID] == 3
        assert movements_cards_by_player[playerID] == 3


def test_play__correct_mov1_card(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 0) else "B" if (x == 2 and y == 2) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov01", isDiscarded=False, playerID=1),
        ]
    )

    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 2 and item["posY"] == 2)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 0}, "destination": {"posX": 2, "posY": 2}},
    )
    assert response.status_code == 201

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 2 and item["posY"] == 2)
    assert origin["color"] == "B"
    assert destination["color"] == "R"


def test_play__incorrect_mov1_card(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 0) else "B" if (x == 2 and y == 2) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov01", isDiscarded=False, playerID=1),
        ]
    )

    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 2 and item["posY"] == 2)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 0}, "destination": {"posX": 3, "posY": 3}},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Movimiento inválido."}

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 2 and item["posY"] == 2)
    assert origin["color"] == "R"
    assert destination["color"] == "B"


def test_play_correct_mov2_card(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 0) else "B" if (x == 0 and y == 2) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov02", isDiscarded=False, playerID=1),
        ]
    )

    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 2)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 0}, "destination": {"posX": 0, "posY": 2}},
    )
    assert response.status_code == 201

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 2)
    assert origin["color"] == "B"
    assert destination["color"] == "R"


def test_play_incorrect_mov2_card(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 0) else "B" if (x == 0 and y == 2) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov02", isDiscarded=False, playerID=1),
        ]
    )

    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 2)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 0}, "destination": {"posX": 1, "posY": 1}},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Movimiento inválido."}

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 2)
    assert origin["color"] == "R"
    assert destination["color"] == "B"


def test_play_correct_mov3_card(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 0) else "B" if (x == 0 and y == 1) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov03", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 1)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 0}, "destination": {"posX": 0, "posY": 1}},
    )
    assert response.status_code == 201

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 1)
    assert origin["color"] == "B"
    assert destination["color"] == "R"


def test_play_incorrect_mov3_card(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 0) else "B" if (x == 0 and y == 1) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov03", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 1)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 0}, "destination": {"posX": 1, "posY": 1}},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Movimiento inválido."}

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 1)
    assert origin["color"] == "R"
    assert destination["color"] == "B"


def test_play_correct_mov4_card(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 0) else "B" if (x == 1 and y == 1) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov04", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 1 and item["posY"] == 1)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 0}, "destination": {"posX": 1, "posY": 1}},
    )
    assert response.status_code == 201

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 1 and item["posY"] == 1)
    assert origin["color"] == "B"
    assert destination["color"] == "R"


def test_play_incorrect_mov4_card(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 0) else "B" if (x == 1 and y == 1) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov04", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 1 and item["posY"] == 1)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 0}, "destination": {"posX": 0, "posY": 1}},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Movimiento inválido."}

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 1 and item["posY"] == 1)
    assert origin["color"] == "R"
    assert destination["color"] == "B"


def test_play_correct_mov5_card_down(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 2) else "B" if (x == 2 and y == 1) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov05", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 2)
    destination = next(item for item in board if item["posX"] == 2 and item["posY"] == 1)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 2}, "destination": {"posX": 2, "posY": 1}},
    )
    assert response.status_code == 201

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 2)
    destination = next(item for item in board if item["posX"] == 2 and item["posY"] == 1)
    assert origin["color"] == "B"
    assert destination["color"] == "R"


def test_play_correct_mov5_card_up(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 2 and y == 1) else "B" if (x == 0 and y == 2) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov05", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 2 and item["posY"] == 1)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 2)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 2, "posY": 1}, "destination": {"posX": 0, "posY": 2}},
    )
    assert response.status_code == 201

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 2 and item["posY"] == 1)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 2)
    assert origin["color"] == "B"
    assert destination["color"] == "R"


def test_play_correct_mov6_card_up(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 2 and y == 1) else "B" if (x == 0 and y == 0) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov06", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 2 and item["posY"] == 1)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 2, "posY": 1}, "destination": {"posX": 0, "posY": 0}},
    )
    assert response.status_code == 201

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 2 and item["posY"] == 1)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    assert origin["color"] == "B"
    assert destination["color"] == "R"


def test_play_correct_mov6_card_down(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 0) else "B" if (x == 2 and y == 1) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov06", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 2 and item["posY"] == 1)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 0}, "destination": {"posX": 2, "posY": 1}},
    )
    assert response.status_code == 201

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 0 and item["posY"] == 0)
    destination = next(item for item in board if item["posX"] == 2 and item["posY"] == 1)
    assert origin["color"] == "B"
    assert destination["color"] == "R"


def test_play_correct_mov7_card(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 3 and y == 1) else "B" if (x == 0 and y == 1) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov07", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 3 and item["posY"] == 1)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 1)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 3, "posY": 1}, "destination": {"posX": 0, "posY": 1}},
    )
    assert response.status_code == 201

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posX"] == 3 and item["posY"] == 1)
    destination = next(item for item in board if item["posX"] == 0 and item["posY"] == 1)
    assert origin["color"] == "B"
    assert destination["color"] == "R"


def test_player_did_not_has_movement_card(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 3 and y == 1) else "B" if (x == 0 and y == 1) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(cardID=1, gameID=1, type="mov07", isDiscarded=True, playerID=2),
            MovementCardDB(cardID=2, gameID=1, type="mov07", isDiscarded=True, playerID=1),
        ]
    )
    db.commit()

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 5, "posY": 1}, "destination": {"posX": 0, "posY": 1}},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "El jugador no tiene la carta de movimiento."}


def test_play_horizontal_mov06(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 1) else "B" if (x == 2 and y == 2) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov06", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posY"] == 1 and item["posX"] == 0)
    destination = next(item for item in board if item["posY"] == 2 and item["posX"] == 2)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 1}, "destination": {"posX": 2, "posY": 2}},
    )
    assert response.status_code == 201

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posY"] == 1 and item["posX"] == 0)
    destination = next(item for item in board if item["posY"] == 2 and item["posX"] == 2)
    assert origin["color"] == "B"
    assert destination["color"] == "R"


def test_play_horizontal_mov05(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 1) else "B" if (x == 2 and y == 0) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov05", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posY"] == 1 and item["posX"] == 0)
    destination = next(item for item in board if item["posY"] == 0 and item["posX"] == 2)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 1}, "destination": {"posX": 2, "posY": 0}},
    )
    assert response.status_code == 201

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posY"] == 1 and item["posX"] == 0)
    destination = next(item for item in board if item["posY"] == 0 and item["posX"] == 2)
    assert origin["color"] == "B"
    assert destination["color"] == "R"


def test_cancel_movement(client, test_db):
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
                board=json.dumps(
                    [
                        {
                            "posX": x,
                            "posY": y,
                            "color": "R" if (x == 0 and y == 1) else "B" if (x == 2 and y == 0) else "G",
                        }
                        for x in range(6)
                        for y in range(6)
                    ]
                ),
            ),
            MovementCardDB(gameID=1, type="mov05", isDiscarded=False, playerID=1),
        ]
    )
    db.commit()

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posY"] == 1 and item["posX"] == 0)
    destination = next(item for item in board if item["posY"] == 0 and item["posX"] == 2)
    assert origin["color"] == "R"
    assert destination["color"] == "B"

    response = client.post(
        "/games/1/movement",
        json={"cardID": 1, "playerID": 1, "origin": {"posX": 0, "posY": 1}, "destination": {"posX": 2, "posY": 0}},
    )
    assert response.status_code == 201

    # Cancel movement

    response = client.delete("/games/1/movement?playerID=1&gameID=1")
    assert response.status_code == 200

    board = db.get(GameDB, 1).board
    board = json.loads(board)
    origin = next(item for item in board if item["posY"] == 1 and item["posX"] == 0)
