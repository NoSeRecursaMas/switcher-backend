from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.database import get_db
from sqlalchemy.orm import Session
from src.lobbys.application.service import LobbyService
from src.players.infrastructure.repository import SQLAlchemyRepository as PlayerSQLAlchemyRepository
from src.lobbys.infrastructure.repository import SQLAlchemyRepository as LobbySQLAlchemyRepository
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest, GetLobbyResponse, GetLobbyData
from src.players.domain.models import PlayerID
from src.lobbys.infrastructure.websockets import ConnectionManager

lobby_router = APIRouter()
websocket_router = APIRouter()

manager = ConnectionManager()


@websocket_router.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, player_id: int, db: Session = Depends(get_db)):
    lobby_repository = LobbySQLAlchemyRepository(db)
    service = LobbyService(lobby_repository)
    player_repository = PlayerSQLAlchemyRepository(db)
    await manager.connect_to_room(room_id=game_id, player_id=player_id, websocket=websocket)
    try:
        await manager.broadcast_to_room(room_id=game_id, message={"type": "UPDATE_ROOM", "payload": {"msg": f"El jugador \"{player_repository.find(player_id).username}\" se ha unido a la sala", "status":
                                                                  service.get_data_lobby(game_id).dict()}})
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


@lobby_router.get("", status_code=200)
def get_lobby(db: Session = Depends(get_db)) -> list[GetLobbyResponse]:
    lobby_repository = LobbySQLAlchemyRepository(db)
    service = LobbyService(lobby_repository)

    lobby_all = service.get_lobby()

    return lobby_all


@lobby_router.get("/{lobby_id}", status_code=200)
def get_data_lobby(lobby_id, db: Session = Depends(get_db)) -> GetLobbyData:

    lobby_repository = LobbySQLAlchemyRepository(db)
    service = LobbyService(lobby_repository)

    lobby_data = service.get_data_lobby(lobby_id)

    return lobby_data
