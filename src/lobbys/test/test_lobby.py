from src.shared.mocks import create_mock_lobby, mock_db, new_mock
import pytest


def test_create_lobby(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db)

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1}


def test_create_lobby_invalid_size(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, name="test_lobby_invalid"*10)

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El valor proporcionado no cumple con los requisitos de longitud permitidos.'}


def test_create_lobby_max_capacity(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, max_players=5)

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El máximo de jugadores permitidos es 4.'}


def test_create_lobby_min_capacity(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, min_players=1)

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El mínimo de jugadores permitidos es 2.'}


def test_create_lobby_error_capacity(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, min_players=5, max_players=4)

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El mínimo de jugadores no puede ser mayor al máximo de jugadores.'}


def test_create_lobby_name_with_space(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, name="test con espacios")

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1}


def test_create_lobby_name_one_character(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, name="t")

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1}


def test_create_lobby_invalid_owner(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, owner_exists=False)

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'El propietario proporcionado no existe.'}


def test_create_lobby_name_not_ascii(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, name="test@Σ")

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El valor proporcionado contiene caracteres no permitidos.'}


def test_create_lobby_name_empty(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, name="")

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El valor proporcionado no cumple con los requisitos de longitud permitidos.'}


def test_create_lobbies_with_same_name(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db)

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 1}

    mock_lobby = create_mock_lobby(mock_db, lobbyID=2, owner=2)

    response = new_mock.post('/lobbys/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'lobbyID': 2}
