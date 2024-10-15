import json

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
            },
        ]

        response.status_code == 201
        response.json() == {"gameID": 1}


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

    game = db.query(GameDB).get(1)
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

    game = db.query(GameDB).get(1)
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
