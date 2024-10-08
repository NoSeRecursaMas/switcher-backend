from src.players.infrastructure.models import Player as PlayerDB
from src.conftest import override_get_db
from src.rooms.infrastructure.models import PlayerRoom
from src.rooms.infrastructure.models import Room as RoomDB

def test_leave_room(client,test_db):
    
    db = next(override_get_db())
    players = [PlayerDB(username=f"player{i}") for i in range(1, 3)]
    db.add_all(players)
    db.commit()

    room = RoomDB(roomName="test_room", minPlayers=2, maxPlayers=4, hostID = players[0].playerID)
    db.add(room)
    db.commit() 
    
    players_room_relations = [
        PlayerRoom(playerID=players[0].playerID, roomID=room.roomID),
        PlayerRoom(playerID=players[1].playerID, roomID=room.roomID),
    ]
    db.add_all(players_room_relations)
    db.commit()
    
    player_id = {
        "playerID": players[1].playerID
    }
    
    response_leave = client.put("/rooms/1/leave", json=player_id)   
    
    players = db.query(PlayerDB).join(PlayerRoom).filter(PlayerRoom.roomID == 1).all()
    players_list = [{"playerID": str(player.playerID), "username": player.username} for player in players]
    
    assert response_leave.status_code == 200
    assert player_id["playerID"] not in [player["playerID"] for player in players_list]




def test_leave_room_player_not_in_room(client,test_db):
    db = next(override_get_db())
    player1 = PlayerDB(username="player1")
    db.add(player1)
    db.commit()
    player2 = PlayerDB(username="player2")
    db.add(player2)
    db.commit()
    player3 = PlayerDB(username="player3")
    db.add(player3)
    db.commit()

    data_room= {
        "playerID": player1.playerID,
        "roomName": "test_room",
        "minPlayers": 2,
        "maxPlayers": 4,
    }
    response_1 = client.post("/rooms/", json=data_room)
    assert response_1.status_code == 201
    assert response_1.json() == {"roomID": 1}

    data_room2= {
        "playerID": player2.playerID,
        "roomName": "test_room2",
        "minPlayers": 2,
        "maxPlayers": 4,
    }
    response_1 = client.post("/rooms/", json=data_room2)
    assert response_1.status_code == 201
    assert response_1.json() == {"roomID": 2}

    PlayerRoom1 = PlayerRoom(playerID=player3.playerID, roomID=1)
    db.add(PlayerRoom1)
    db.commit()
    

    data_leave_room = {
        "playerID": player3.playerID
    }

    response_leave = client.put("/rooms/2/leave", json=data_leave_room)
    assert response_leave.status_code == 404
    assert response_leave.json() == {"detail": "El jugador no se encuentra en la sala."}

def test_leave_room_room_not_found(client,test_db):
    db = next(override_get_db())
    player1 = PlayerDB(username="player1")
    db.add(player1)
    db.commit()
    player2 = PlayerDB(username="player2")
    db.add(player2)
    db.commit()

    data_room= {
        "playerID": player1.playerID,
        "roomName": "test_room",
        "minPlayers": 2,
        "maxPlayers": 4,
    }
    response_1 = client.post("/rooms/", json=data_room)
    assert response_1.status_code == 201
    assert response_1.json() == {"roomID": 1}

    PlayerRoom1 = PlayerRoom(playerID=player2.playerID, roomID=1)
    db.add(PlayerRoom1)
    db.commit()
    

    data_leave_room = {
        "playerID": player2.playerID
    }

    response_leave = client.put("/rooms/3/leave", json=data_leave_room)
    assert response_leave.status_code == 404
    assert response_leave.json() == {"detail": "La sala proporcionada no existe."}


def test_leave_room_owner(client,test_db):
    db = next(override_get_db())
    player1 = PlayerDB(username="player1")
    db.add(player1)
    db.commit()

    data_room= {
        "playerID": player1.playerID,
        "roomName": "test_room",
        "minPlayers": 2,
        "maxPlayers": 4,
    }
    response_1 = client.post("/rooms/", json=data_room)
    assert response_1.status_code == 201
    assert response_1.json() == {"roomID": 1}

    data_leave_room = {
        "playerID": player1.playerID
    }

    response_leave = client.put("/rooms/1/leave", json=data_leave_room)
    assert response_leave.status_code == 404
    assert response_leave.json() == {"detail": "El propietario no puede abandonar la sala."}
