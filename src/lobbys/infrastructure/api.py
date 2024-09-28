from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.database import get_db
from sqlalchemy.orm import Session
from src.lobbys.application.service import LobbyService
from src.players.infrastructure.repository import SQLAlchemyRepository as PlayerSQLAlchemyRepository
from src.lobbys.infrastructure.repository import SQLAlchemyRepository as LobbySQLAlchemyRepository
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest
from src.lobbys.infrastructure.lobby_websockets import ConnectionManager
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest, GetLobbyResponse, GetLobbyData

lobby_router = APIRouter()
websocket_router = APIRouter()

manager = ConnectionManager()  

@websocket_router.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, player_id: int):
    await manager.connect_to_room(room_id=game_id, player_id=player_id, websocket=websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "message":
                await manager.broadcast_to_room(room_id=game_id, message=data["content"])
            elif data["type"] == "get_room_info":
                await manager.broadcast_to_room(room_id=game_id, message=get_data_lobby(game_id))
    except WebSocketDisconnect:
        await manager.disconnect_from_room(room_id=game_id, player_id=player_id, websocket=websocket)  


@lobby_router.post("", status_code=201)
async def create_lobby(lobby_data: CreateLobbyRequest, db: Session = Depends(get_db)) -> LobbyResponse:
    lobby_repository = LobbySQLAlchemyRepository(db)
    player_repository = PlayerSQLAlchemyRepository(db)
    service = LobbyService(lobby_repository, player_repository)
    lobby = service.create_lobby(lobby_data)
    lobby_data_response = get_data_lobby(lobby.roomID, db)
    await manager.broadcast_to_room(lobby.roomID, lobby_data_response)
    return lobby


@lobby_router.get("",status_code=200)
def get_lobby (db: Session = Depends(get_db)) -> list[GetLobbyResponse]:
    lobby_repository = LobbySQLAlchemyRepository(db)
    service = LobbyService(lobby_repository)

    lobby_all = service.get_lobby()

    return lobby_all


@lobby_router.get("/{lobby_id}",status_code=200)
def get_data_lobby(lobby_id, db: Session = Depends(get_db)) -> GetLobbyData:

    lobby_repository = LobbySQLAlchemyRepository(db)
    service = LobbyService(lobby_repository)

    lobby_data = service.get_data_lobby(lobby_id)

    return lobby_data
