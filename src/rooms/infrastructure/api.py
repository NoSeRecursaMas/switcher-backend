from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from src.database import get_db
from sqlalchemy.orm import Session
from src.rooms.application.service import RoomService
from src.players.infrastructure.repository import SQLAlchemyRepository as PlayerSQLAlchemyRepository
from src.rooms.infrastructure.repository import SQLAlchemyRepository as RoomSQLAlchemyRepository
from src.rooms.domain.models import RoomID, RoomCreationRequest, RoomExtendedInfo, RoomPublicInfo
from src.players.domain.models import PlayerID
from src.rooms.infrastructure.websockets import ConnectionManager
from typing import List

room_router = APIRouter()
websocket_router = APIRouter()

manager = ConnectionManager()


@websocket_router.websocket("/ws/{game_id}/{playerID}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, playerID: int, db: Session = Depends(get_db)):
    room_repository = RoomSQLAlchemyRepository(db)
    service = RoomService(room_repository)
    player_repository = PlayerSQLAlchemyRepository(db)
    await manager.connect_to_room(roomID=game_id, playerID=playerID, websocket=websocket)
    try:
        await manager.broadcast_to_room(roomID=game_id, message={"type": "update_room", "payload": {"msg": f"Sala creada por {player_repository.get(playerID).username}", "status":
                                                                                                    service.get_public_info(game_id).dict()}})
        while True:
            data = await websocket.receive_json()
            if data["type"] == "message":
                await manager.broadcast_to_room(roomID=game_id, message=data["content"])
            elif data["type"] == "exit":
                await manager.disconnect_from_room(roomID=game_id, playerID=playerID, websocket=websocket)
    except WebSocketDisconnect:
        await manager.disconnect_from_room(roomID=game_id, playerID=playerID, websocket=websocket)


@room_router.post("", status_code=201)
def create_room(room_data: RoomCreationRequest, db: Session = Depends(get_db)) -> RoomID:
    service = RoomService(RoomSQLAlchemyRepository(db),
                          PlayerSQLAlchemyRepository(db))
    room = service.create_room(room_data)
    return room


@room_router.put("/{roomID}/leave", status_code=200)
def leave_room(roomID: int, playerID: PlayerID, db: Session = Depends(get_db)) -> None:
    service = RoomService(RoomSQLAlchemyRepository(db),
                          PlayerSQLAlchemyRepository(db))

    service.leave_room(roomID, playerID.playerID)


@room_router.get("", status_code=200)
def get_all_rooms(db: Session = Depends(get_db)) -> List[RoomExtendedInfo]:
    service = RoomService(RoomSQLAlchemyRepository(db))

    rooms = service.get_all_rooms()

    return rooms
