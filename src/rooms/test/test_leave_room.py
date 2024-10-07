from src.players.infrastructure.models import Player as PlayerDB
from src.conftest import TestingSessionLocal
from src.conftest import override_get_db
from src.rooms.infrastructure.models import PlayerRoom

def test_leave_room(client,test_db):
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
    response_leave = client.put("/rooms/1/leave", json=data_leave_room)
    print(response_leave.json())
    assert response_leave.status_code == 200

    response_get = client.get("/rooms/")
    assert response_get.status_code == 200
    assert response_get.json() == [{
            "roomID": 1,
            "roomName": "test_room",
            "maxPlayers": 4,
            "actualPlayers": 1, 
            "started": False,
            "private": False,
        }]

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
    print(PlayerRoom1)
    db.add(PlayerRoom1)
    db.commit()
    

    data_leave_room = {
        "playerID": player3.playerID
    }

    response_leave = client.put("/rooms/2/leave", json=data_leave_room)
    print(response_leave.json())
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
    print(response_leave.json())
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
    print(response_leave.json())
    assert response_leave.status_code == 404
    assert response_leave.json() == {"detail": "El propietario no puede abandonar la sala."}


# def test_leave_room_owner(new_mock, mock_db):
#     player_repo_patch, room_repo_patch = leave_room_mock(is_owner=True)

#     with player_repo_patch, room_repo_patch:
#         roomID = 1
#         playerID = {"playerID": 1}

#         reponse = new_mock.put(f"/rooms/{roomID}/leave", json=playerID)

#         assert reponse.status_code == 405
#         assert reponse.json() == {"detail": "El propietario no puede abandonar la sala."}
