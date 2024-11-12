from src.conftest import override_get_db
from src.players.infrastructure.models import Player as PlayerDB
from src.rooms.infrastructure.models import PlayerRoom as PlayerRoomDB
from src.rooms.infrastructure.models import Room as RoomDB


def test_create_room(client, test_db):
    db = next(override_get_db())
    db.add(PlayerDB(username="test"))
    db.commit()

    data_room = {
        "playerID": 1,
        "roomName": "test_room",
        "minPlayers": 2,
        "maxPlayers": 4,
    }

    response = client.post("/rooms/", json=data_room)
    assert response.status_code == 201
    assert response.json() == {"roomID": 1}


def test_create_room_invalid_size(client, test_db):
    room_data = {
        "playerID": 1,
        "roomName": "test" * 10,
        "minPlayers": 2,
        "maxPlayers": 4,
    }
    response = client.post("/rooms/", json=room_data)
    assert response.status_code == 422
    assert (
        response.json().get("detail")[0]["msg"]
        == "El roomName proporcionado no cumple con los requisitos de longitud permitidos."
    )


def test_create_room_max_capacity(client, test_db):
    room_data = {
        "playerID": 1,
        "roomName": "test",
        "minPlayers": 2,
        "maxPlayers": 5,
    }

    response = client.post("/rooms/", json=room_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "El máximo de jugadores permitidos es 4."}


def test_create_room_min_capacity(client, test_db):
    room_data = {
        "playerID": 1,
        "roomName": "test",
        "minPlayers": 1,
        "maxPlayers": 4,
    }

    response = client.post("/rooms/", json=room_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "El mínimo de jugadores permitidos es 2."}


def test_create_room_error_capacity(client, test_db):
    room_data = {
        "playerID": 1,
        "roomName": "test",
        "minPlayers": 5,
        "maxPlayers": 4,
    }

    response = client.post("/rooms/", json=room_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "El mínimo de jugadores no puede ser mayor al máximo de jugadores."}


def test_create_room_name_with_space(client, test_db):
    db = next(override_get_db())
    db.add(PlayerDB(username="testroomwithspace"))
    db.commit()

    room_data = {
        "playerID": 1,
        "roomName": "test con espacios",
        "minPlayers": 2,
        "maxPlayers": 4,
    }

    response = client.post("/rooms/", json=room_data)
    assert response.status_code == 201
    assert response.json() == {"roomID": 1}


def test_create_room_name_one_character(client, test_db):
    db = next(override_get_db())
    db.add(PlayerDB(username="testroomonecharacter"))
    db.commit()

    room_data = {
        "playerID": 1,
        "roomName": "A",
        "minPlayers": 2,
        "maxPlayers": 4,
    }
    response = client.post("/rooms/", json=room_data)
    assert response.status_code == 201
    assert response.json() == {"roomID": 1}


def test_create_room_invalid_owner(client, test_db):
    db = next(override_get_db())
    db.add(PlayerDB(username="testroominvalidowner"))
    db.commit()

    room_data = {
        "playerID": 2,
        "roomName": "test",
        "minPlayers": 2,
        "maxPlayers": 4,
    }

    response = client.post("/rooms/", json=room_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "El jugador no existe."}


def test_create_room_name_not_ascii(client, test_db):
    room_data = {
        "playerID": 1,
        "roomName": "test@Σ",
        "minPlayers": 2,
        "maxPlayers": 4,
    }
    response = client.post("/rooms/", json=room_data)
    assert response.status_code == 422
    assert response.json().get("detail")[0]["msg"] == "El roomName proporcionado contiene caracteres no permitidos."


def test_create_room_name_empty(client, test_db):
    room_data = {
        "playerID": 1,
        "roomName": "",
        "minPlayers": 2,
        "maxPlayers": 4,
    }

    response = client.post("/rooms/", json=room_data)
    assert response.status_code == 422
    assert (
        response.json().get("detail")[0]["msg"]
        == "El roomName proporcionado no cumple con los requisitos de longitud permitidos."
    )


def test_create_rooms_with_same_name(client, test_db):
    db = next(override_get_db())
    player1 = PlayerDB(username="player1")
    db.add(player1)
    db.commit()

    room_data_1 = {
        "playerID": player1.playerID,
        "roomName": "test_room",
        "minPlayers": 2,
        "maxPlayers": 4,
    }

    response_1 = client.post("/rooms/", json=room_data_1)
    assert response_1.status_code == 201
    assert response_1.json() == {"roomID": 1}

    player2 = PlayerDB(username="player2")
    db.add(player2)
    db.commit()

    room_data_2 = {
        "playerID": player2.playerID,
        "roomName": "test_room",
        "minPlayers": 2,
        "maxPlayers": 4,
    }

    response_2 = client.post("/rooms/", json=room_data_2)
    assert response_2.status_code == 201
    assert response_2.json() == {"roomID": 2}
    assert response_1.json() != response_2.json()


def test_create_room_with_password(client, test_db):
    db = next(override_get_db())
    player1 = PlayerDB(username="player1")
    db.add(player1)
    db.commit()

    data_room = {
        "playerID": 1,
        "roomName": "test_room",
        "minPlayers": 2,
        "maxPlayers": 4,
        "password": "1234",
    }

    response = client.post("/rooms/", json=data_room)
    assert response.status_code == 201
    assert response.json() == {"roomID": 1}


def test_create_room_send_update_room_list_ws(client, test_db):
    db = next(override_get_db())
    player1 = PlayerDB(username="player1")
    db.add(player1)
    db.commit()

    data_room = {
        "playerID": 1,
        "roomName": "test_room",
        "minPlayers": 2,
        "maxPlayers": 4,
    }

    with client.websocket_connect(f"/rooms/{player1.playerID}") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == []

        response = client.post("/rooms/", json=data_room)

        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == [
            {
                "roomID": 1,
                "roomName": "test_room",
                "maxPlayers": 4,
                "actualPlayers": 1,
                "started": False,
                "private": False,
                "playersID": [1],
            },
        ]
        assert response.status_code == 201
        assert response.json() == {"roomID": 1}
