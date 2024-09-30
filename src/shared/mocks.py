from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db
import pytest
from src.lobbys.domain.models import GetLobbyData

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
    mock_lobby.playerID = playerID

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
        mock_lobby.password = 'password' if lobby['private'] else None
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


def list_mock_data_lobby(mock_db, lobbies_data):
    # Mock para simular la tabla Lobby
    mock_lobby = MagicMock()
    mock_lobbyplayerID = lobbies_data[0]["hostID"]
    # Aseguramos que sea un string
    mock_lobby.name = lobbies_data[0]["roomName"]
    mock_lobby.roomID = lobbies_data[0]["roomID"]
    mock_lobby.minPlayers = lobbies_data[0]["minPlayers"]
    mock_lobby.maxPlayers = lobbies_data[0]["maxPlayers"]

    # Mock para la consulta de Lobby
    mock_lobby_query = MagicMock()
    mock_lobby_query.filter.return_value.first.return_value = mock_lobby

    # Simulamos la consulta para obtener los jugadores del lobby
    mock_player_query = MagicMock()
    mock_player_query.join.return_value.filter.return_value.all.return_value = [
        MagicMock(playerID=player[0], username=player[1]) for player in lobbies_data[0]["players"]
    ]

    # Asignamos los mocks a la base de datos mockeada
    mock_db.query.side_effect = [mock_lobby_query, mock_player_query]


def join_lobby_mock(player_exists=True, lobby_exists=True, full=False):
    mock_player_repo = MagicMock()
    mock_lobby_repo = MagicMock()
    
    if full:
        data_lobby = GetLobbyData(
            hostID=1,
            roomName="test",
            roomID=1,
            minPlayers=2,
            maxPlayers=3,
            players=[{"playerID": "1", "username": "test"}, {"playerID": "2", "username": "test2"}, {"playerID": "3", "username": "test3"}]
        )
    else:
        data_lobby = GetLobbyData(
            hostID=1,
            roomName="test",
            roomID=1,
            minPlayers=2,
            maxPlayers=4,
            players=[{"playerID": "1", "username": "test"}, {"playerID": "2", "username": "test2"}]
        ) 
    
    
    mock_player_repo.find = MagicMock(return_value=player_exists)
    mock_lobby_repo.find = MagicMock(return_value=lobby_exists)
    mock_lobby_repo.get_data_lobby = MagicMock(return_value=data_lobby)
    
    return (
        patch("src.lobbys.infrastructure.api.LobbySQLAlchemyRepository", return_value=mock_lobby_repo),
        patch("src.lobbys.infrastructure.api.PlayerSQLAlchemyRepository", return_value=mock_player_repo)
    )


def leave_lobby_mock(player_exists=True, lobby_exists=True, player_in_lobby=True, is_owner=False):
    mock_player_repo = MagicMock()
    mock_lobby_repo = MagicMock()

    mock_player_repo.find = MagicMock(return_value=player_exists)
    mock_lobby_repo.get_data_lobby = MagicMock(return_value=lobby_exists)
    mock_lobby_repo.player_in_lobby = MagicMock(return_value=player_in_lobby)
    mock_lobby_repo.is_owner = MagicMock(return_value=is_owner)

    return patch('src.lobbys.infrastructure.api.LobbySQLAlchemyRepository', return_value=mock_lobby_repo), \
        patch('src.lobbys.infrastructure.api.PlayerSQLAlchemyRepository',
              return_value=mock_player_repo)

