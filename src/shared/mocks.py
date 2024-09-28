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
    mock_db.refresh.side_effect = lambda x: setattr(
        x, 'playerID', player_id) if hasattr(x, 'playerID') else None
    mock_db.query().filter().first.return_value = mock_player
    return {
        "playerID": player_id,
        "username": username
    }


def create_mock_lobby(mock_db, owner_exists=True, roomID=1, playerID=1, roomName="test_lobby", minPlayers=2, maxPlayers=4, password="") -> dict:
    mock_lobby = MagicMock()
    mock_lobby.roomID = roomID
    mock_lobby.roomName = roomName
    mock_lobby.minPlayers = minPlayers
    mock_lobby.maxPlayers = maxPlayers
    mock_lobby.password = password
    mock_lobby.owner = playerID

    if owner_exists:
        create_mock_player(mock_db, player_id=playerID, username="test")
    else:
        mock_db.query().filter().first.return_value = None

    mock_db.add.return_value = mock_lobby
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, 'roomID', roomID)

    mock_lobby = {
        "playerID": playerID,
        "roomName": roomName,
        "minPlayers": minPlayers,
        "maxPlayers": maxPlayers,
        "password": password
    }

    return mock_lobby


def list_mock_lobby(mock_db, lobbies_data, players_data):
    def create_mock_lobby(lobby):
        mock_lobby = MagicMock()
        mock_lobby.roomID = lobby['roomID']
        mock_lobby.name = lobby['roomName']
        mock_lobby.maxPlayers = lobby['maxPlayers']
        mock_lobby.actualPlayers = lobby['actualPlayers']
        mock_lobby.started = lobby['started']
        mock_lobby.password = 'password' if not lobby['private'] else None
        mock_lobby.players = [MagicMock()
                              for _ in range(lobby['actualPlayers'])]
        return mock_lobby

    mock_lobbies = [create_mock_lobby(lobby) for lobby in lobbies_data]

    # Crear mocks para los métodos all(), order_by() y filter()
    query_mock_lobby = MagicMock()
    query_mock_lobby.order_by.return_value.all.return_value = mock_lobbies

    def filter_mock(*args):
        roomID = args[0].right.value
        # Buscar el lobby correspondiente por roomID
        players_in_room = [p for p in players_data if p['roomID'] == roomID]
        return MagicMock(all=MagicMock(return_value=players_in_room))

    query_mock_player = MagicMock()
    query_mock_player.filter.side_effect = filter_mock

    # Asignar el query_mock al método query de mock_db
    mock_db.query.side_effect = lambda model: query_mock_lobby if model.__name__ == 'Lobby' else query_mock_player
