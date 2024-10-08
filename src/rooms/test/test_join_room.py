from src.players.infrastructure.models import Player as PlayerDB
from src.conftest import override_get_db
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

    room = RoomDB(roomName="test_room1", minPlayers=2, maxPlayers=4, hostID = players[0].playerID)
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
