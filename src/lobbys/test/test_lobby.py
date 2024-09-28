from src.shared.mocks import create_mock_lobby,list_mock_lobby, mock_db, new_mock,list_mock_data_lobby
import pytest



def test_create_lobby(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1}


def test_create_lobby_invalid_size(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, name="test_lobby_invalid"*10)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El valor proporcionado no cumple con los requisitos de longitud permitidos.'}


def test_create_lobby_max_capacity(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, max_players=5)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El máximo de jugadores permitidos es 4.'}


def test_create_lobby_min_capacity(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, min_players=1)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El mínimo de jugadores permitidos es 2.'}


def test_create_lobby_error_capacity(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, min_players=5, max_players=4)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El mínimo de jugadores no puede ser mayor al máximo de jugadores.'}


def test_create_lobby_name_with_space(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, name="test con espacios")

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1}


def test_create_lobby_name_one_character(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, name="t")

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1}


def test_create_lobby_invalid_owner(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, owner_exists=False)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'El propietario proporcionado no existe.'}


def test_create_lobby_name_not_ascii(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, name="test@Σ")

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El valor proporcionado contiene caracteres no permitidos.'}


def test_create_lobby_name_empty(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, name="")

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El valor proporcionado no cumple con los requisitos de longitud permitidos.'}


def test_create_lobbies_with_same_name(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1}

    mock_lobby = create_mock_lobby(mock_db, lobbyID=2, owner=2)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 2}


def test_get_all_lobbies(new_mock, mock_db):

    lobbies_data = [
        {"roomID": 1, "roomName": "test_lobby", "maxPlayers": 4,"actualPlayers":3,"started":False, "private": False}
    ]
    list_mock_lobby(mock_db,lobbies_data)


    response = new_mock.get('/rooms/')
    print("Response JSON:", response.json())  
    assert response.status_code == 200
    assert response.json() == [{'roomID': 1, 'roomName': 'test_lobby', 'maxPlayers': 4,'actualPlayers':3,'started':False, 'private': False}]



def test_get_four_lobbies(new_mock, mock_db):

    lobbies_data = [
        {"roomID": 1, "roomName": "test_lobby", "maxPlayers": 4,"actualPlayers":2,"started":False, "private": False},
        {"roomID": 2, "roomName": "test_lobby2", "maxPlayers": 4,"actualPlayers":2,"started":False, "private": False},
        {"roomID": 3, "roomName": "test_lobby3", "maxPlayers": 4,"actualPlayers":2,"started":False, "private": False},
        {"roomID": 4, "roomName": "test_lobby4", "maxPlayers": 4,"actualPlayers":2,"started":False, "private": False}
    ]

    list_mock_lobby(mock_db, lobbies_data)

    response = new_mock.get('/rooms/')
    assert response.status_code == 200
    print("Response JSON:", response.json())
    assert response.json() == [
        {"roomID": 1, "roomName": "test_lobby", "maxPlayers": 4,"actualPlayers":2,"started":False, "private": False},
        {"roomID": 2, "roomName": "test_lobby2", "maxPlayers": 4,"actualPlayers":2,"started":False, "private": False},
        {"roomID": 3, "roomName": "test_lobby3", "maxPlayers": 4,"actualPlayers":2,"started":False, "private": False},
        {"roomID": 4, "roomName": "test_lobby4", "maxPlayers": 4,"actualPlayers":2,"started":False, "private": False}]


def test_get_lobbies_empty(new_mock, mock_db):

    lobbies_data = []
    list_mock_lobby(mock_db, lobbies_data)

    response = new_mock.get('/rooms/')
    assert response.status_code == 200
    assert response.json() == []

def test_get_data_lobby(new_mock, mock_db):
    lobbies_data = [{"hostID": 1, "roomName": "test_lobby", "roomID": 1, "minPlayers": 2, "maxPlayers": 4, "players": [[1, "test"], [2, "test2"]]}]
    
    # Simulamos los datos de la base de datos
    list_mock_data_lobby(mock_db, lobbies_data)

    # Realizamos la solicitud
    response = new_mock.get('/rooms/1')

    # Verificamos el resultado
    assert response.status_code == 200
    assert response.json() == {
        "hostID": 1,
        "roomName": "test_lobby",
        "roomID": 1,
        "minPlayers": 2,
        "maxPlayers": 4,
        "players": [[1, "test"], [2, "test2"]]
    }
