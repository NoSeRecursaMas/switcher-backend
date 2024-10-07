import pytest

from src.shared.mocks import create_mock_player, mock_db, new_mock


def test_create_player(new_mock, mock_db):
    mock_player = create_mock_player(mock_db, playerID=1, username="mensio")
    response = new_mock.post("/players", json=mock_player)
    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "mensio"}


def test_create_player_invalid_size(new_mock):
    response = new_mock.post("/players", json={"username": ""})
    assert response.status_code == 422
    assert (
        response.json().get("detail")[0]["msg"]
        == "El username proporcionado no cumple con los requisitos de longitud permitidos."
    )


def test_create_player_long_name(new_mock):
    long_name = "A" * 33
    response = new_mock.post("/players", json={"username": long_name})
    assert response.status_code == 422
    assert (
        response.json().get("detail")[0]["msg"]
        == "El username proporcionado no cumple con los requisitos de longitud permitidos."
    )


def test_create_player_non_ascii(new_mock):
    response = new_mock.post("/players", json={"username": "nombre_con_ñ"})
    assert response.status_code == 422
    assert response.json().get("detail")[0]["msg"] == "El username proporcionado contiene caracteres no permitidos."


def test_create_player_one_character(new_mock, mock_db):
    mock_player = create_mock_player(mock_db, playerID=1, username="A")
    response = new_mock.post("/players", json=mock_player)
    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "A"}


def test_create_player_with_spaces(new_mock, mock_db):
    mock_player = create_mock_player(mock_db, playerID=1, username="S A N   T I")
    response = new_mock.post("/players", json=mock_player)
    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "S A N   T I"}


def test_create_two_players_with_same_name(new_mock, mock_db):
    mock_player_1 = create_mock_player(mock_db, playerID=1, username="mensio")
    response1 = new_mock.post("/players", json=mock_player_1)
    assert response1.status_code == 201
    player1 = response1.json()
    assert player1["username"] == "mensio"

    mock_player_2 = create_mock_player(mock_db, playerID=2, username="mensio")
    response2 = new_mock.post("/players", json=mock_player_2)
    assert response2.status_code == 201
    player2 = response2.json()

    assert player1["playerID"] == 1
    assert player2["playerID"] == 2
    assert player1["playerID"] != player2["playerID"]
