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


def create_mock_player(mock_db, player_id, username):
    mock_player = MagicMock()
    mock_player.playerID = player_id
    mock_player.username = username
    mock_db.refresh.side_effect = lambda x: setattr(x, 'playerID', player_id) if hasattr(x, 'playerID') else None
    mock_db.query().filter().first.return_value = mock_player
    return {
        "playerID": player_id,
        "username": username
    }

    
def create_mock_lobby(mock_db, owner_exists=True, lobbyID=1, name="test_lobby", min_players=2, max_players=4, owner=1, password=""):
    mock_lobby = MagicMock()
    mock_lobby.lobbyID = lobbyID
    mock_lobby.name = name
    mock_lobby.min_players = min_players
    mock_lobby.max_players = max_players
    mock_lobby.password = password
    mock_lobby.owner = owner

    if owner_exists:
        create_mock_player(mock_db, player_id=owner, username="test")
    else:
        mock_db.query().filter().first.return_value = None

    mock_db.add.return_value = mock_lobby
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, 'lobbyID', lobbyID)

    return {
        "lobbyID": lobbyID,
        "name": name,
        "min_players": min_players,
        "max_players": max_players,
        "password": password,
        "owner": owner
    }

def list_mock_lobby(mock_db, lobbies_data):
    mock_lobbies = []

    for lobby in lobbies_data:
        mock_lobby = MagicMock()
        mock_lobby.lobbyID = lobby['lobbyID']
        mock_lobby.name = lobby['roomName']
        mock_lobby.max_players = lobby['maxPlayers']
        mock_lobby.actual_players = lobby['actualPlayers']
        mock_lobby.started = lobby['started']
        mock_lobby.private = lobby['private']
        # Simular la relación de jugadores (puedes ajustar la cantidad de jugadores en cada lobby)
        mock_lobby.players = [MagicMock() for _ in range(lobby['actualPlayers'])]  # Simula una lista de jugadores
        mock_lobbies.append(mock_lobby)

    # Mock para el método all()
    list_lobbies_mock = MagicMock()
    list_lobbies_mock.all.return_value = mock_lobbies

    # Mock para el método order_by()
    query_mock = MagicMock()
    query_mock.order_by.return_value = list_lobbies_mock

    # Mock para el método filter(), que se utiliza en get_actual_players
    def filter_mock(*args, **kwargs):
        # Extraer el lobbyID del filtro
        lobbyID = args[0].right.value
        # Encontrar el lobby con ese lobbyID
        for mock_lobby in mock_lobbies:
            if mock_lobby.lobbyID == lobbyID:
                return MagicMock(first=MagicMock(return_value=mock_lobby))
        return MagicMock(first=MagicMock(return_value=None))  # Si no se encuentra, devolver None

    query_mock.filter.side_effect = filter_mock

    # Asignar query_mock al método query de mock_db
    mock_db.query.return_value = query_mock