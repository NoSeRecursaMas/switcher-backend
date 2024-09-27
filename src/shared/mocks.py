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