from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.database import get_db
from src.main import app

from src.rooms.domain.models import RoomPublicInfo

client = TestClient(app)


@pytest.fixture(scope="function")
def mock_db():
    with patch("src.database.SessionLocal") as mock_session:
        db_session = mock_session.return_value

        db_session.commit = MagicMock()
        db_session.add = MagicMock()
        db_session.refresh = MagicMock()

        yield db_session


@pytest.fixture(scope="function")
def new_mock(mock_db):
    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    yield client
    app.dependency_overrides.clear()


def create_mock_player(mock_db, playerID, username):
    mock_player = MagicMock()
    mock_player.playerID = playerID
    mock_player.username = username
    mock_db.refresh.side_effect = lambda x: (
        setattr(x, "playerID", playerID) if hasattr(x, "playerID") else None)
    mock_db.query().filter().first.return_value = mock_player

    return {"playerID": playerID, "username": username}


def create_mock_room(
    mock_db,
    owner_exists=True,
    roomID=1,
    playerID=1,
    roomName="test_room",
    minPlayers=2,
    maxPlayers=4,
    password="",
) -> dict:
    mock_room = {
        "roomID": roomID,
        "playerID": playerID,
        "roomName": roomName,
        "minPlayers": minPlayers,
        "maxPlayers": maxPlayers,
        "password": password,
    }

    if owner_exists:
        create_mock_player(mock_db, playerID=playerID, username="test")
    else:
        mock_db.query().filter().first.return_value = None

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, "roomID", roomID)

    return mock_room


def list_mock_room(mock_db, lobbies_data, players_data):
    def create_mock_room(room):
        mock_room = MagicMock()
        mock_room.roomID = room["roomID"]
        mock_room.roomName = room["roomName"]
        mock_room.maxPlayers = room["maxPlayers"]
        mock_room.actualPlayers = room["actualPlayers"]
        mock_room.started = room["started"]
        mock_room.password = "password" if room["private"] else None
        mock_room.players = [MagicMock() for _ in range(room["actualPlayers"])]
        return mock_room

    mock_lobbies = [create_mock_room(room) for room in lobbies_data]

    # Crear mocks para los métodos all(), order_by() y filter()
    query_mock_room = MagicMock()
    query_mock_room.order_by.return_value.all.return_value = mock_lobbies

    def filter_mock(*args):
        roomID = args[0].right.value
        # Buscar el room correspondiente por roomID
        players_in_room = [p for p in players_data if p["roomID"] == roomID]
        return MagicMock(all=MagicMock(return_value=players_in_room))

    query_mock_player = MagicMock()
    query_mock_player.filter.side_effect = filter_mock

    # Asignar el query_mock al método query de mock_db
    mock_db.query.side_effect = lambda model: (
        query_mock_room if model.__name__ == "Room" else query_mock_player)


def list_mock_data_room(mock_db, lobbies_data):
    # Mock para simular la tabla Room
    mock_room = MagicMock()
    mock_roomplayerID = lobbies_data[0]["hostID"]
    # Aseguramos que sea un string
    mock_room.roomName = lobbies_data[0]["roomName"]
    mock_room.roomID = lobbies_data[0]["roomID"]
    mock_room.minPlayers = lobbies_data[0]["minPlayers"]
    mock_room.maxPlayers = lobbies_data[0]["maxPlayers"]

    # Mock para la consulta de Room
    mock_room_query = MagicMock()
    mock_room_query.filter.return_value.first.return_value = mock_room

    # Simulamos la consulta para obtener los jugadores del room
    mock_player_query = MagicMock()
    mock_player_query.join.return_value.filter.return_value.all.return_value = [
        MagicMock(playerID=player[0], username=player[1]) for player in lobbies_data[0]["Players"]
    ]

    # Asignamos los mocks a la base de datos mockeada
    mock_db.query.side_effect = [mock_room_query, mock_player_query]


def leave_room_mock(player_exists=True, room_exists=True, is_player_in_room=True, is_owner=False):
    mock_player_repo = MagicMock()
    mock_room_repo = MagicMock()

    mock_player_repo.get = MagicMock(return_value=player_exists)
    mock_room_repo.get = MagicMock(return_value=room_exists)
    mock_room_repo.is_player_in_room = MagicMock(
        return_value=is_player_in_room)
    mock_room_repo.is_owner = MagicMock(return_value=is_owner)

    return patch(
        "src.rooms.infrastructure.api.RoomSQLAlchemyRepository",
        return_value=mock_room_repo,
    ), patch(
        "src.rooms.infrastructure.api.PlayerSQLAlchemyRepository",
        return_value=mock_player_repo,
    )


def join_room_mock(player_exists=True, room_exists=True, full=False):
    mock_player_repo = MagicMock()
    mock_room_repo = MagicMock()

    if full:
        data_room = RoomPublicInfo(
            hostID=1,
            roomName="test",
            roomID=1,
            minPlayers=2,
            maxPlayers=3,
            players=[{"playerID": "1", "username": "test"}, {
                "playerID": "2", "username": "test2"}, {"playerID": "3", "username": "test3"}]
        )
    else:
        data_room = RoomPublicInfo(
            hostID=1,
            roomName="test",
            roomID=1,
            minPlayers=2,
            maxPlayers=4,
            players=[{"playerID": "1", "username": "test"},
                     {"playerID": "2", "username": "test2"}]
        )

    mock_player_repo.get = MagicMock(return_value=player_exists)
    mock_room_repo.get = MagicMock(return_value=room_exists)
    mock_room_repo.get_public_info = MagicMock(return_value=data_room)

    return (
        patch("src.rooms.infrastructure.api.RoomSQLAlchemyRepository",
              return_value=mock_room_repo),
        patch("src.rooms.infrastructure.api.PlayerSQLAlchemyRepository",
              return_value=mock_player_repo)
    )
