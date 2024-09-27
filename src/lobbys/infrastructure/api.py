from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.database import get_db
from sqlalchemy.orm import Session
from src.lobbys.application.service import LobbyService
from src.players.infrastructure.repository import SQLAlchemyRepository as PlayerSQLAlchemyRepository
from src.lobbys.infrastructure.repository import SQLAlchemyRepository as LobbySQLAlchemyRepository
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest
from src.lobbys.infrastructure.websockets import ConnectionManager
from src.players.domain.models import PlayerID


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
            elif data["type"] == "exit":
                await manager.disconnect_from_room(room_id=game_id, player_id=player_id, websocket=websocket)
    except WebSocketDisconnect:
        await manager.disconnect_from_room(room_id=game_id, player_id=player_id, websocket=websocket)


@lobby_router.post("", status_code=201)
def create_lobby(lobby_data: CreateLobbyRequest, db: Session = Depends(get_db)) -> LobbyResponse:
    lobby_repository = LobbySQLAlchemyRepository(db)
    player_repository = PlayerSQLAlchemyRepository(db)
    service = LobbyService(lobby_repository, player_repository)

    lobby = service.create_lobby(lobby_data)
    return lobby


@lobby_router.put("/{lobby_id}/leave", status_code=200)
def leave_lobby(lobby_id: int, player_id: PlayerID, db: Session = Depends(get_db)) -> None:
    lobby_repository = LobbySQLAlchemyRepository(db)
    player_repository = PlayerSQLAlchemyRepository(db)
    service = LobbyService(lobby_repository, player_repository)

    service.leave_lobby(lobby_id, player_id.playerID)

    return None
