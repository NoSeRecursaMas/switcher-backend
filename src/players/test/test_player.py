from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.main import app
from src.players.domain.models import PlayerUsername, PlayerResponse
from src.database import get_db
import pytest

client = TestClient(app)

# Fixture para mockear la sesión de base de datos
@pytest.fixture(scope="module")
def mock_db():
    with patch("src.database.SessionLocal", autospec=True) as mock_session:
        db_session = mock_session.return_value
        db_session.commit = MagicMock()
        db_session.refresh = MagicMock()
        db_session.add = MagicMock()
        yield db_session


# Sobrescribir la dependencia de FastAPI para usar el mock en lugar de la base de datos real
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