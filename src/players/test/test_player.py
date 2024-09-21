from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.main import app
from src.players.domain.models import PlayerUsername, PlayerResponse
from src.database import get_db
import pytest

client = TestClient(app)

# fixture to mock the database session
@pytest.fixture(scope="module")
def mock_db():
    with patch("src.database.SessionLocal", autospec=True) as mock_session:
        db_session = mock_session.return_value
        db_session.commit = MagicMock()
        db_session.refresh = MagicMock()
        db_session.add = MagicMock()
        yield db_session

# fixture to override the get_db dependency
@pytest.fixture(scope="module")
def test_client(mock_db):
    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    yield client

def test_create_player(test_client, mock_db):
   
    mock_player_infra = MagicMock()
    mock_player_infra.playerID = 1
    mock_player_infra.username = "hola"

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, "playerID", 1)
    
    response = test_client.post("/players", json={"username": "hola"})

    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "hola"}

def test_create_player_invalid_size(test_client):
    response = test_client.post("/players", json={"username": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "El nombre debe tener entre 1 y 32 caracteres"}

def test_create_player_non_ascii(test_client):
    response = test_client.post("/players", json={"username": "nombre_con_ñ"})
    assert response.status_code == 400
    assert response.json() == {"detail": "El nombre debe ser ASCII"}

def test_create_player_one_character(test_client):
    response = test_client.post("/players", json={"username": "A"})
    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "A"}

def test_create_player_long_name(test_client):
    long_name = "A" * 33
    response = test_client.post("/players", json={"username": long_name})
    assert response.status_code == 400
    assert response.json() == {"detail": "El nombre debe tener entre 1 y 32 caracteres"}

def test_create_player_with_spaces(test_client):
    response = test_client.post("/players", json={"username": "S A N     T I"})
    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "S A N     T I"}

def test_create_two_players_with_same_name(test_client, mock_db):
    player_id_counter = 1

    def mock_add(player):
        nonlocal player_id_counter
        player.playerID = player_id_counter
        player_id_counter += 1

    mock_db.add.side_effect = mock_add
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: None

    response1 = test_client.post("/players", json={"username": "duplicate_name"})
    assert response1.status_code == 201
    player1 = response1.json()
    assert player1["username"] == "duplicate_name"

    response2 = test_client.post("/players", json={"username": "duplicate_name"})
    assert response2.status_code == 201
    player2 = response2.json()
    assert player2["username"] == "duplicate_name"
    assert player1["playerID"] != player2["playerID"]