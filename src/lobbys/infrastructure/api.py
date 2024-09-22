from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.database import get_db
from sqlalchemy.orm import Session
from src.lobbys.application.service import LobbyService
from src.players.infrastructure.repository import SQLAlchemyRepository as PlayerSQLAlchemyRepository
from src.lobbys.infrastructure.repository import SQLAlchemyRepository as LobbySQLAlchemyRepository
from src.lobbys.domain.models import LobbyResponse, CreteLobbyRequest
from src.lobbys.infrastructure.lobby_websockets import ConnectionManager

router = APIRouter()

manager = ConnectionManager

@router.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, player_id: int):
    await manager.connect_to_room(room_id=game_id,player_id=player_id,websocket=websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "update":
                pass
    except WebSocketDisconnect:
        manager.disconnect_from_room(room_id=game_id,player_id=player_id,websocket=websocket)


@router.post("", status_code=201)
def create_lobby(lobby_data: CreteLobbyRequest, db: Session = Depends(get_db)) -> LobbyResponse:
    lobby_repository = LobbySQLAlchemyRepository(db)
    player_repository = PlayerSQLAlchemyRepository(db)
    service = LobbyService(lobby_repository, player_repository)

    lobby = service.create_lobby(lobby_data)
    return lobby
