from src.conftest import override_get_db
from src.players.infrastructure.models import Player as PlayerDB
from src.rooms.infrastructure.models import Room as RoomDB
from src.rooms.infrastructure.models import PlayerRoom as PlayerRoomDB
from src.games.infrastructure.models import FigureCard as FigureCardDB
from src.games.infrastructure.models import MovementCard as MovementCardDB

def test_create_game(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID = players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()

    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})
    assert response.status_code == 201
    assert response.json() == {"gameID": 1}

def test_create_game_cards(client, test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID = players[0].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()

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

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID = players[0].playerID)
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

def test_player_is_not_owner(client,test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID = players[1].playerID)
    db.add(room)
    db.commit()

    players_room_relations = [
        PlayerRoomDB(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoomDB(playerID=players[1].playerID, roomID=room.roomID),
    ]

    db.add_all(players_room_relations)
    db.commit()

    response = client.post(f"/games/{room.roomID}", json={"playerID": players[0].playerID})
    assert response.status_code == 405
    assert response.json() == {"detail": "Solo el propietario puede iniciar la partida."}

def test_game_room_not_exists(client,test_db):
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID = players[1].playerID)
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

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID = players[0].playerID)
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
    

    