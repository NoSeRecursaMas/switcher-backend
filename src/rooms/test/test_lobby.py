from src.shared.mocks import create_mock_room, list_mock_room, mock_db, new_mock, list_mock_data_room
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import WebSocket
from src.main import app
import pytest
from src.rooms.infrastructure.websockets import ConnectionManager


def mock_get_data_room(game_id):
    return {"roomID": game_id, "info": "Room Info"}


@pytest.fixture
def mock_websocket():
    return MagicMock(spec=WebSocket)


@pytest.mark.asyncio
@patch('src.rooms.application.service.RoomService.get_public_info', new_callable=AsyncMock)
@patch.object(ConnectionManager, 'broadcast_to_room', new_callable=AsyncMock)
async def test_websocket_broadcast_correctly(mock_broadcast_to_room, mock_get_data_room, mock_websocket):
    mock_websocket.receive_json = AsyncMock(
        return_value={"type": "get_room_info"})

    mock_get_data_room.return_value = {"roomID": 1, "info": "Room Info"}

    manager = ConnectionManager()

    await manager.connect_to_room(roomID=1, playerID=1, websocket=mock_websocket)

    await manager.broadcast_to_room(roomID=1, message=await mock_get_data_room(1))

    mock_broadcast_to_room.assert_any_call(
        roomID=1, message={"roomID": 1, "info": "Room Info"})

    data = await mock_websocket.receive_json()
    if data["type"] == "get_room_info":
        await manager.broadcast_to_room(roomID=1, message=await mock_get_data_room(1))

    mock_broadcast_to_room.assert_any_call(
        roomID=1, message={"roomID": 1, "info": "Room Info"})


@pytest.mark.asyncio
@patch.object(ConnectionManager, 'send_personal_message', new_callable=AsyncMock)
async def test_websocket_send_personal_message(mock_send_personal_message, mock_websocket):
    mock_websocket.receive_json = AsyncMock(return_value={"type": "message"})

    manager = ConnectionManager()

    await manager.connect_to_room(roomID=1, playerID=1, websocket=mock_websocket)

    await manager.send_personal_message(message={"msg": "test"}, playerID=1)

    mock_send_personal_message.assert_any_call(
        message={"msg": "test"}, playerID=1)

    data = await mock_websocket.receive_json()
    if data["type"] == "message":
        await manager.send_personal_message(message={"msg": "test"}, playerID=1)

    mock_send_personal_message.assert_any_call(
        message={"msg": "test"}, playerID=1)


def test_create_room_invalid_size(new_mock, mock_db):

    mock_room = create_mock_room(mock_db, roomName="test_room_invalid"*10)

    response = new_mock.post('/rooms/', json=mock_room)
    assert response.status_code == 422
    assert response.json().get(
        "detail")[0]["msg"] == 'El roomName proporcionado no cumple con los requisitos de longitud permitidos.'


def test_create_room_max_capacity(new_mock, mock_db):

    mock_room = create_mock_room(mock_db, maxPlayers=5)

    response = new_mock.post('/rooms/', json=mock_room)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El máximo de jugadores permitidos es 4.'}


def test_create_room_min_capacity(new_mock, mock_db):

    mock_room = create_mock_room(mock_db, minPlayers=1)

    response = new_mock.post('/rooms/', json=mock_room)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El mínimo de jugadores permitidos es 2.'}


def test_create_room_error_capacity(new_mock, mock_db):

    mock_room = create_mock_room(mock_db, minPlayers=5, maxPlayers=4)

    response = new_mock.post('/rooms/', json=mock_room)
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'El mínimo de jugadores no puede ser mayor al máximo de jugadores.'}


def test_create_room_name_with_space(new_mock, mock_db):

    mock_room = create_mock_room(mock_db, roomName="test con espacios")

    response = new_mock.post('/rooms/', json=mock_room)
    assert response.status_code == 201
    assert response.json() == {'roomID': 1}


def test_create_room_name_one_character(new_mock, mock_db):

    mock_room = create_mock_room(mock_db, roomName="t")

    response = new_mock.post('/rooms/', json=mock_room)
    assert response.status_code == 201
    assert response.json() == {'roomID': 1}


def test_create_room_invalid_owner(new_mock, mock_db):

    mock_room = create_mock_room(mock_db, owner_exists=False)

    response = new_mock.post('/rooms/', json=mock_room)
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'El jugador proporcionado no existe.'}


def test_create_room_name_not_ascii(new_mock, mock_db):

    mock_room = create_mock_room(mock_db, roomName="test@Σ")

    response = new_mock.post('/rooms/', json=mock_room)
    assert response.status_code == 422
    assert response.json().get(
        "detail")[0]["msg"] == 'El roomName proporcionado contiene caracteres no permitidos.'


def test_create_room_name_empty(new_mock, mock_db):

    mock_room = create_mock_room(mock_db, roomName="")

    response = new_mock.post('/rooms/', json=mock_room)
    assert response.status_code == 422
    assert response.json().get(
        "detail")[0]["msg"] == 'El roomName proporcionado no cumple con los requisitos de longitud permitidos.'


def test_create_lobbies_with_same_name(new_mock, mock_db):

    mock_room = create_mock_room(mock_db)

    response = new_mock.post('/rooms/', json=mock_room)
    assert response.status_code == 201
    assert response.json() == {'roomID': 1}

    mock_room = create_mock_room(mock_db, roomID=2, playerID=2)

    response = new_mock.post('/rooms/', json=mock_room)
    assert response.status_code == 201
    assert response.json() == {'roomID': 2}


def test_get_all_lobbies(new_mock, mock_db):

    lobbies_data = [
        {"roomID": 1, "roomName": "test_room", "maxPlayers": 4,
         "actualPlayers": 3, "started": False, "private": False}
    ]

    players_data = [
        {"playerID": 1, "roomID": 1},
        {"playerID": 2, "roomID": 1},
        {"playerID": 3, "roomID": 1}
    ]
    list_mock_room(mock_db, lobbies_data, players_data)

    response = new_mock.get('/rooms/')

    assert response.status_code == 200
    assert response.json() == [{'roomID': 1, 'roomName': 'test_room',
                                'maxPlayers': 4, 'actualPlayers': 3, 'started': False, 'private': False}]


def test_get_four_lobbies(new_mock, mock_db):

    lobbies_data = [
        {"roomID": 1, "roomName": "test_room", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 2, "roomName": "test_room2", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 3, "roomName": "test_room3", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 4, "roomName": "test_room4", "maxPlayers": 4,
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

    list_mock_room(mock_db, lobbies_data, players_data)

    response = new_mock.get('/rooms/')
    assert response.status_code == 200

    assert response.json() == [
        {"roomID": 1, "roomName": "test_room", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 2, "roomName": "test_room2", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 3, "roomName": "test_room3", "maxPlayers": 4,
            "actualPlayers": 2, "started": False, "private": False},
        {"roomID": 4, "roomName": "test_room4", "maxPlayers": 4, "actualPlayers": 2, "started": False, "private": False}]


def test_get_lobbies_empty(new_mock, mock_db):

    lobbies_data = []
    players_data = []
    list_mock_room(mock_db, lobbies_data, players_data)

    response = new_mock.get('/rooms/')
    assert response.status_code == 200
    assert response.json() == []
