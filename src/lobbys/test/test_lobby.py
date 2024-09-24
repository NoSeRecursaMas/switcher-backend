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
        
        # Simula los metodos de la sesion de la base de datos.
        db_session.commit = MagicMock()
        db_session.add = MagicMock()
        db_session.refresh = MagicMock()

        #Retorna el objeto simulado db_session que será utilizado en las pruebas.
        yield db_session       


#Reemplaza la dependencia original get_db 
#De FastAPI para que retorne el mock mock_db en lugar de la sesión real de base de datos.
@pytest.fixture(scope='module')
def new_mock(mock_db):
    def override_get_db():
        yield mock_db 

    app.dependency_overrides[get_db] = override_get_db
    
    #devuelve el cliente client con la base de datos mockeada.
    yield client

    app.dependency_overrides.clear()


def test_create_lobby(new_mock, mock_db):
    mock_player = MagicMock()
    mock_player.playerID = 1
    mock_player.username = 'test'

    mock_db.query().filter().first.return_value = mock_player

    mock_db.add.return_value = None
    mock_db.commit.return_value = None

    #agrega un atributo lobbyID con valor 1 al objeto pasado
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



def test_create_lobby_invalid_size(new_mock):
    mock_lobby = {
        "lobbyName": "test_lobby_invalid"*10,
        "min_players": 2,
        "max_players": 4,
        "password": "",
        "owner": 1
    }

    response = new_mock.post('/lobbys/', json=mock_lobby)
    print(response.json())
    assert response.status_code == 400
    assert response.json() == {'detail': 'El valor proporcionado no cumple con los requisitos de longitud permitidos.'}

'''
def test_create_lobby_max_capacity(new_mock):
    mock_lobby = {
        "lobbyName": "test_max_capacity",
        "min_players": 2,
        "max_players": 10,
        "password": "",
        "owner": 1
    }


    response = new_mock.post('/lobbys/', json=mock_lobby)
    print(response.json())
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
'''


## ACA HAY UNA HARCODEADA, SI AGREGAMOS LOS SIGUIENTES DOS TESTS, ABAJO DEL ARCHIVO
## PUEDE QUE SE ROMPAN, PUES EN UN TEST ESTOY DICIENDO QUE EL OWNER 1 ES INVALIDO
def test_create_lobby_name_with_space(new_mock):
    
    mock_lobby ={
        "lobbyName": "test con espacios",
        "min_players": 2,
        "max_players": 4,
        "password": "",
        "owner": 1
    }

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1}

def test_create_lobby_name_one_character(new_mock):

    mock_lobby = {
        "lobbyName": "t",
        "min_players": 2,
        "max_players": 4,
        "password": "",
        "owner": 1
    }

    response = new_mock.post('/lobbys/', json=mock_lobby)
    print(response.json())
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1}

def test_create_lobby_invalid_owner(new_mock, mock_db):

    mock_db.query().filter().first.return_value = None  # Simulamos que el owner no existe

    mock_lobby = {
        "lobbyName": "test_lobby_not_owner",
        "min_players": 2,
        "max_players": 4,
        "password": "",
        "owner": 1
    }

    response = new_mock.post('/lobbys/', json=mock_lobby)
    print(response.json())
    assert response.status_code == 404
    assert response.json() == {'detail': 'El valor proporcionado no cumple con el owner indicado'}



def test_create_lobby_name_not_ascii(new_mock):

    mock_lobby = {
        "lobbyName": "test@Σ",
        "min_players": 2,
        "max_players": 4,
        "password": "",
        "owner": 1
    }

    response = new_mock.post('/lobbys/', json=mock_lobby)
    print(response.json())
    assert response.status_code == 400
    assert response.json() == {'detail': 'El valor proporcionado contiene caracteres no permitidos.'}


def test_create_lobby_name_empty(new_mock):
    mock_lobby = {
        "lobbyName": "",
        "min_players": 2,
        "max_players": 4,
        "password": "",
        "owner": 2
    }
    
    response = new_mock.post('/lobbys/', json=mock_lobby)
    print(response.json())
    assert response.status_code == 400
    assert response.json() == {'detail': 'El valor proporcionado no cumple con los requisitos de longitud permitidos.'}





'''
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