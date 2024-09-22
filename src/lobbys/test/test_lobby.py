from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import MagicMock, patch
from src.database import get_db
import pytest


client = TestClient (app)

@pytest.fixture(scope='module')
def mock_db():
    with patch("src.database.SessionLocal") as mock_session:
        db_session = mock_session.return_value
        
        db_session.commit = MagicMock()
        db_session.add = MagicMock()
        db_session.refresh = MagicMock()

        # Simular el comportamiento de query().filter().first()


        yield db_session       


@pytest.fixture(scope='module')
def new_mock(mock_db):
    def override_get_db():
        yield mock_db 

    app.dependency_overrides[get_db] = override_get_db
    yield client

    app.dependency_overrides.clear()

def test_create_lobby(new_mock, mock_db):
    mock_player = MagicMock()
    mock_player.playerID = 1
    mock_player.username = 'test'

    mock_db.query().filter().first.return_value = mock_player

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, 'lobbyID', 1)

    mock_lobby = {
        "lobbyName": "test_lobby",
        "min_players": 2,
        "max_players": 4,
        "password": "",
        "owner": 1
    }

    response = new_mock.post('/lobbys/', json=mock_lobby)
    
    print(response.json())

    assert response.status_code == 201
    
    assert response.json() == {'lobbyID': 1}


'''
def test_create_lobby_invalid_size(new_lobby):
    mock_lobby = MagicMock()
    mocklobbyID = 1
    mockowner = 1
    mocklobbyName = 'Messi'*10
    mockmin_players = 2
    mockmax_players = 4
    

    response = new_lobby.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {'detail': 'El nombre es muy largo.'}


def test_create_lobby_max_capacity(new_lobby):
    mock_lobby = MagicMock()
    mock_lobby.lobbyID = 1
    mock_lobby.owner = 1
    mock_lobby.lobbyName = 'test'
    mock_lobby.min_players = 2
    mock_lobby.max_players = 5

    response = new_lobby.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {'detail': 'El valor proporcionado no cumple con los requisitos de jugadores permitidos.'}


def test_create_lobby_min_capacity(new_lobby):
    mock_lobby = MagicMock()
    mock_lobby.lobbyID = 1
    mock_lobby.owner = 1
    mock_lobby.lobbyName = 'test'
    mock_lobby.min_players = 1
    mock_lobby.max_players = 4

    response = new_lobby.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {'detail': 'El valor proporcionado no cumple con los requisitos de jugadores permitidos.'}
    
def test_create_lobby_error_capacity(new_lobby):
    mock_lobby = MagicMock()
    mock_lobby.lobbyID = 1
    mock_lobby.owner = 1
    mock_lobby.lobbyName = 'test'
    mock_lobby.min_players = 4
    mock_lobby.max_players = 2

    response = new_lobby.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {'detail': 'Capacidad minima mayor a la capacidad maxima.'}

def test_create_lobby_invalid_owner(new_lobby):
    mock_lobby = MagicMock()
    mock_lobby.lobbyID = 1
    mock_lobby.owner = None
    mock_lobby.lobbyName = 'test'
    mock_lobby.min_players = 2
    mock_lobby.max_players = 4

    response = new_lobby.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {'detail': 'El valor proporcionado no cumple con el owner indicado'}

def test_create_lobby_name_not_ascii(new_lobby):
    mock_lobby = MagicMock()
    mock_lobby.lobbyID = 1
    mock_lobby.owner = 1
    mock_lobby.lobbyName = 'test@'
    mock_lobby.min_players = 2
    mock_lobby.max_players = 4

    response = new_lobby.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {'detail': 'El valor proporcionado contiene caracteres no permitidos.'}

def test_create_lobby_name_empty(new_lobby):
    mock_lobby = MagicMock()
    mock_lobby.lobbyID = 1
    mock_lobby.owner = 1
    mock_lobby.lobbyName = ''
    mock_lobby.min_players = 2
    mock_lobby.max_players = 4

    response = new_lobby.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {'detail': 'No se permiten lobbys sin nombre.'}

def test_create_lobby_name_with_space(new_lobby):
    mock_lobby = MagicMock()
    mock_lobby.lobbyID = 1
    mock_lobby.owner = 1
    mock_lobby.lobbyName = 'test test'
    mock_lobby.min_players = 2
    mock_lobby.max_players = 4

    response = new_lobby.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1, 'owner': 1, 'lobbyName': 'test test', 'min_players': 2, 'max_players': 4, 'password': None}

def test_create_lobby_name_one_character(new_lobby):
    mock_lobby = MagicMock()
    mock_lobby.lobbyID = 1
    mock_lobby.owner = 1
    mock_lobby.lobbyName = 't'
    mock_lobby.min_players = 2
    mock_lobby.max_players = 4

    response = new_lobby.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1, 'owner': 1, 'lobbyName': 't', 'min_players': 2, 'max_players': 4, 'password': None}


def test_create_lobbies_with_same_name(new_lobby,mock_lobby_db):
    mock_lobby1 = MagicMock()
    mock_lobby1.lobbyID = 1
    mock_lobby1.owner = 1
    mock_lobby1.lobbyName = 'test_equal'
    mock_lobby1.min_players = 2
    mock_lobby1.max_players = 4

    mock_lobby_db.add.return_value = None
    mock_lobby_db.commit.return_value = None
    mock_lobby_db.refresh.return_value = lambda x: setattr(x, 'lobbyID', 1)

    response1 = new_lobby.post('/lobbys/', json=mock_lobby1)
    assert response1.status_code == 201
    assert response1.json() == {'lobbyID': 1, 'owner': 1, 'lobbyName': 'test_equal', 'min_players': 2, 'max_players': 4, 'password': None}

    mock_lobby2 = MagicMock()
    mock_lobby2.owner = 1
    mock_lobby2.lobbyID = 2
    mock_lobby2.lobbyName = 'test_equal'
    mock_lobby2.min_players = 2
    mock_lobby2.max_players = 4

    mock_lobby_db.add.return_value = None
    mock_lobby_db.commit.return_value = None
    mock_lobby_db.refresh.return_value = lambda x: setattr(x, 'lobbyID', 2)

    response2 = new_lobby.post('/lobbys/', json=mock_lobby2)
    assert response2.status_code == 201
    assert response2.json() == {'lobbyID': 2, 'owner': 1, 'lobbyName': 'test_equal', 'min_players': 2, 'max_players': 4, 'password': None}
    '''