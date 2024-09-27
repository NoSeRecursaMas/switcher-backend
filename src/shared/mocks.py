from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db
import pytest


client = TestClient(app)


@pytest.fixture(scope='function')
def mock_db():
    with patch("src.database.SessionLocal") as mock_session:
        db_session = mock_session.return_value

        db_session.commit = MagicMock()
        db_session.add = MagicMock()
        db_session.refresh = MagicMock()

        yield db_session


@pytest.fixture(scope='function')
def new_mock(mock_db):
    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    yield client
    app.dependency_overrides.clear()


def create_mock_player(mock_db, player_id=1, username='test'):
    mock_player = MagicMock()
    mock_player.playerID = player_id
    mock_player.username = username
    mock_db.query().filter().first.return_value = mock_player


def create_mock_lobby(mock_db, owner_exists=True, lobbyID=1, name="test_lobby", min_players=2, max_players=4, owner=1, password=""):

    if owner_exists:
        mock_db.refresh.side_effect = lambda x: setattr(x, 'lobbyID', lobbyID)
        create_mock_player(mock_db, player_id=owner)
    else:
        mock_db.query().filter().first.return_value = None

    return {
        "name": name,
        "min_players": min_players,
        "max_players": max_players,
        "password": password,
        "owner": owner
    }

def list_mock_lobby (mock_db, lobbies_data):
    
    mock_lobbies =  []

    for lobby in lobbies_data:
        mock_lobby = MagicMock()
        mock_lobby.lobbyID = lobby['lobbyID']
        mock_lobby.name = lobby['roomName']
        mock_lobby.max_players = lobby['max_players']
        mock_lobby.private = lobby['private']
        mock_lobbies.append(mock_lobby)
  # Mock para el método all()
    list_lobbies_mock = MagicMock()
    list_lobbies_mock.all.return_value = mock_lobbies

    # Mock para el método order_by()
    query_mock = MagicMock()
    query_mock.order_by.return_value = list_lobbies_mock

    # Asignar query_mock al método query de mock_db
    mock_db.query.return_value = query_mock