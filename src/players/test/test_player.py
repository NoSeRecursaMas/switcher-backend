import logging
from src.shared.mocks import create_mock_player, mock_db, new_mock
import pytest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_create_player(new_mock, mock_db):

    mock_player = create_mock_player(mock_db, player_id=1, username="mensio")
    print(mock_player)
    response = new_mock.post("/players", json=mock_player)
    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "mensio"}

def test_create_player_invalid_size(new_mock):
    response = new_mock.post("/players", json={"username": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "El nombre debe tener entre 1 y 32 caracteres"}

def test_create_player_non_ascii(new_mock):
    response = new_mock.post("/players", json={"username": "nombre_con_ñ"})
    assert response.status_code == 400
    assert response.json() == {"detail": "El nombre debe ser ASCII"}

def test_create_player_one_character(new_mock, mock_db):
    mock_player = create_mock_player(mock_db, player_id=1, username="A")
    response = new_mock.post("/players", json=mock_player)
    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "A"}

def test_create_player_long_name(new_mock):
    long_name = "A" * 33
    response = new_mock.post("/players", json={"username": long_name})
    assert response.status_code == 400
    assert response.json() == {"detail": "El nombre debe tener entre 1 y 32 caracteres"}

def test_create_player_with_spaces(new_mock, mock_db):
    mock_player = create_mock_player(mock_db, player_id=1, username="S A N     T I")
    response = new_mock.post("/players", json=mock_player)
    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "S A N     T I"}

def test_create_two_players_with_same_name(new_mock, mock_db):

    mock_player_1 = create_mock_player(mock_db, player_id=1, username="mensio")

    response1 = new_mock.post("/players", json=mock_player_1)
    assert response1.status_code == 201
    player1 = response1.json()
    assert player1["username"] == "mensio"


    mock_player_2 = create_mock_player(mock_db, player_id=2, username="mensio")
    response2 = new_mock.post("/players", json=mock_player_2)
    assert response2.status_code == 201
    player2 = response2.json()

    assert player1["playerID"] != player2["playerID"]                                                                                                                                                                                                                            