from src.main import app
from src.database import get_db
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from src.database import Base
import pytest
from fastapi.websockets import WebSocketDisconnect
from src.rooms.infrastructure.models import Room as RoomDB, PlayerRoom
from src.players.infrastructure.models import Player as PlayerDB

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_connect_to_room_list_websocket_user_not_exist(test_db):
    db = TestingSessionLocal()
    db.add(PlayerDB(username="test user"))
    db.commit()
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect("/rooms/3") as websocket:
            websocket.receive_json()
    assert e.value.code == 4004
    assert "no existe" in e.value.reason
    assert "jugador" in e.value.reason


def test_connect_to_room_list_websocket_player_exist_and_no_rooms(test_db):
    db = TestingSessionLocal()
    player = PlayerDB(username="test user")
    db.add(player)
    db.commit()

    with client.websocket_connect("/rooms/1") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == []

def test_connect_to_room_list_websocket_player_exist_and_has_rooms(test_db):
    db = TestingSessionLocal()
    db.add_all([
        PlayerDB(username="test user"),
        PlayerDB(username="test user 2"),
        PlayerDB(username="test user 3"),
        PlayerDB(username="test user 4"),
        PlayerDB(username="test user 5"),
        RoomDB(roomName="test room", minPlayers=2, maxPlayers=4, hostID=1),
        RoomDB(roomName="test room 2", minPlayers=2, maxPlayers=4, hostID=2),
    ])

    db.commit()

    db.add_all([
        PlayerRoom(playerID=1, roomID=1),
        PlayerRoom(playerID=1, roomID=2),
        PlayerRoom(playerID=2, roomID=1),
    ])

    db.commit()

    with client.websocket_connect("/rooms/5") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert data["payload"] == [
            {
                "roomID": 1,
                "roomName": "test room",
                "maxPlayers": 4,
                "actualPlayers": 2,
                "started": False,
                "private": False,
            },
            {
                "roomID": 2,
                "roomName": "test room 2",
                "maxPlayers": 4,
                "actualPlayers": 1,
                "started": False,
                "private": False,
            },
        ]
  
  

