from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.database import get_db
from src.players.domain.models import PlayerID
from src.players.infrastructure.repository import (
    SQLAlchemyRepository as PlayerSQLAlchemyRepository,
)
from src.rooms.infrastructure.repository import (
    SQLAlchemyRepository as RoomSQLAlchemyRepository
)
from src.rooms.application.service import RoomService
from src.rooms.domain.models import (
    RoomCreationRequest,
    RoomExtendedInfo,
    RoomID,
    RoomPublicInfo,
)
from src.rooms.infrastructure.websockets import ConnectionManager

room_router = APIRouter()
websocket_router = APIRouter()

manager = ConnectionManager()


@ websocket_router.websocket("/ws/{game_id}/{playerID}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, playerID: int, db: Session = Depends(get_db)):
    lobby_repository = RoomSQLAlchemyRepository(db)
    service = RoomService(lobby_repository)
    player_repository = PlayerSQLAlchemyRepository(db)
    await manager.connect_to_room(roomID=game_id, playerID=playerID, websocket=websocket)
    try:
        await manager.broadcast_to_room(roomID=game_id, message={"type": "UPDATE_ROOM", "payload": {"msg": f"El jugador \"{player_repository.get(playerID).username}\" se ha unido a la sala", "status":
                                                                                                    service.get_public_info(game_id).model_dump()}})
        while True:
            data = await websocket.receive_json()
            if data["type"] == "message":
                await manager.broadcast_to_room(roomID=game_id, message=data["content"])
            elif data["type"] == "exit":
                await manager.disconnect_from_room(roomID=game_id, playerID=playerID, websocket=websocket)
    except WebSocketDisconnect:
        await manager.disconnect_from_room(roomID=game_id, playerID=playerID, websocket=websocket)
        await manager.broadcast_to_room(roomID=game_id, message={"type": "UPDATE_ROOM", "payload": {"msg": f"El jugador \"{player_repository.get(playerID).username}\" ha abandonado la sala", "status":
                                                                                                    service.get_public_info(game_id).model_dump()}})


@ room_router.post("", status_code=201)
def create_room(room_data: RoomCreationRequest, db_session: Session = Depends(get_db)) -> RoomID:
    service = RoomService(RoomSQLAlchemyRepository(
        db_session), PlayerSQLAlchemyRepository(db_session))
    room = service.create_room(room_data)
    return room


@ room_router.put("/{roomID}/leave", status_code=200)
def leave_room(roomID: int, playerID: PlayerID, db_session: Session = Depends(get_db)) -> None:
    service = RoomService(RoomSQLAlchemyRepository(
        db_session), PlayerSQLAlchemyRepository(db_session))

    service.leave_room(roomID, playerID.playerID)


@ room_router.get("", status_code=200)
def get_all_rooms(db_session: Session = Depends(get_db)) -> List[RoomExtendedInfo]:
    service = RoomService(RoomSQLAlchemyRepository(db_session))

    rooms = service.get_all_rooms()

    return rooms


@ room_router.put("/{roomID}/join", status_code=200)
def join_room(roomID: int, playerID: PlayerID, db_session: Session = Depends(get_db)) -> None:
    service = RoomService(RoomSQLAlchemyRepository(
        db_session), PlayerSQLAlchemyRepository(db_session))

    service.join_room(roomID, playerID.playerID)
