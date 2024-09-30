from src.shared.mocks import create_mock_lobby, list_mock_lobby, mock_db, new_mock, list_mock_data_lobby
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import WebSocket
from src.main import app
import pytest
from src.lobbys.infrastructure.websockets import ConnectionManager


def mock_get_data_lobby(game_id):
    return {"room_id": game_id, "info": "Room Info"}


@pytest.fixture
def mock_websocket():
    return MagicMock(spec=WebSocket)


@pytest.mark.asyncio
@patch('src.lobbys.infrastructure.api.get_data_lobby', side_effect=mock_get_data_lobby)
@patch.object(ConnectionManager, 'broadcast_to_room', new_callable=AsyncMock)
async def test_websocket_broadcast_correctly(mock_broadcast_to_room, mock_get_data_lobby, mock_websocket):
    mock_websocket.receive_json = AsyncMock(
        return_value={"type": "get_room_info"})

    manager = ConnectionManager()

    await manager.connect_to_room(room_id=1, player_id=1, websocket=mock_websocket)

    await manager.broadcast_to_room(room_id=1, message=mock_get_data_lobby(1))

    mock_broadcast_to_room.assert_any_call(
        room_id=1, message={"room_id": 1, "info": "Room Info"})

    data = await mock_websocket.receive_json()
    if data["type"] == "get_room_info":
        await manager.broadcast_to_room(room_id=1, message=mock_get_data_lobby(1))

    mock_broadcast_to_room.assert_any_call(
        room_id=1, message={"room_id": 1, "info": "Room Info"})

# test de send_personal_message websocket


@pytest.mark.asyncio
@patch.object(ConnectionManager, 'send_personal_message', new_callable=AsyncMock)
async def test_websocket_send_personal_message(mock_send_personal_message, mock_websocket):
    mock_websocket.receive_json = AsyncMock(return_value={"type": "message"})

    manager = ConnectionManager()

    await manager.connect_to_room(room_id=1, player_id=1, websocket=mock_websocket)

    await manager.send_personal_message(message={"msg": "test"}, player_id=1)

    mock_send_personal_message.assert_any_call(
        message={"msg": "test"}, player_id=1)

    data = await mock_websocket.receive_json()
    if data["type"] == "message":
        await manager.send_personal_message(message={"msg": "test"}, player_id=1)

    mock_send_personal_message.assert_any_call(
        message={"msg": "test"}, player_id=1)


def test_create_lobby_invalid_size(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, roomName="test_lobby_invalid"*10)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El valor proporcionado no cumple con los requisitos de longitud permitidos.'}


def test_create_lobby_max_capacity(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, maxPlayers=5)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El máximo de jugadores permitidos es 4.'}


def test_create_lobby_min_capacity(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, minPlayers=1)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El mínimo de jugadores permitidos es 2.'}


def test_create_lobby_error_capacity(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, minPlayers=5, maxPlayers=4)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El mínimo de jugadores no puede ser mayor al máximo de jugadores.'}


def test_create_lobby_name_with_space(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, roomName="test con espacios")

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'roomID': 1}


def test_create_lobby_name_one_character(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, roomName="t")

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'roomID': 1}


def test_create_lobby_invalid_owner(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, owner_exists=False)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'El jugador proporcionado no existe.'}


def test_create_lobby_name_not_ascii(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, roomName="test@Σ")

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El valor proporcionado contiene caracteres no permitidos.'}


def test_create_lobby_name_empty(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db, roomName="")

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El valor proporcionado no cumple con los requisitos de longitud permitidos.'}


def test_create_lobbies_with_same_name(new_mock, mock_db):

    mock_lobby = create_mock_lobby(mock_db)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'roomID': 1}

    mock_lobby = create_mock_lobby(mock_db, roomID=2, playerID=2)

    response = new_mock.post('/rooms/', json=mock_lobby)
    assert response.status_code == 201
    assert response.json() == {'roomID': 2}


def test_get_all_lobbies(new_mock, mock_db):

    lobbies_data = [
        {"roomID": 1, "roomName": "test_lobby", "maxPlayers": 4,
         "actualPlayers": 3, "started": False, "private": False}
    ]

    players_data = [
        {"playerID": 1, "roomID": 1},
        {"playerID": 2, "roomID": 1},
        {"playerID": 3, "roomID": 1}
    ]
    list_mock_lobby(mock_db, lobbies_data, players_data)

    response = new_mock.get('/rooms/')

    assert response.status_code == 200
    assert response.json() == [{'roomID': 1, 'roomName': 'test_lobby',
                                'maxPlayers': 4, 'actualPlayers': 3, 'started': False, 'private': False}]


def test_get_four_lobbies(new_mock, mock_db):

    lobbies_data = [
        {"roomID": 1, "roomName": "test_lobby", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 2, "roomName": "test_lobby2", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 3, "roomName": "test_lobby3", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 4, "roomName": "test_lobby4", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False}
    ]

    players_data = [
        {"playerID": 1, "roomID": 1},
        {"playerID": 2, "roomID": 1},
        {"playerID": 1, "roomID": 2},
        {"playerID": 2, "roomID": 2},
        {"playerID": 1, "roomID": 3},
        {"playerID": 2, "roomID": 3},
        {"playerID": 1, "roomID": 4},
        {"playerID": 2, "roomID": 4}
    ]

    list_mock_lobby(mock_db, lobbies_data, players_data)

    response = new_mock.get('/rooms/')
    assert response.status_code == 200

    assert response.json() == [
        {"roomID": 1, "roomName": "test_lobby", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 2, "roomName": "test_lobby2", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 3, "roomName": "test_lobby3", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 4, "roomName": "test_lobby4", "maxPlayers": 4, "actualPlayers": 2, "started": False, "private": False}]


def test_get_lobbies_empty(new_mock, mock_db):

    lobbies_data = []
    players_data = []
    list_mock_lobby(mock_db, lobbies_data, players_data)

    response = new_mock.get('/rooms/')
    assert response.status_code == 200
    assert response.json() == []
