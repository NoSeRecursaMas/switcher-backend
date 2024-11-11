from typing import Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.database import get_db
from src.players.domain.models import PlayerID
from src.players.infrastructure.repository import (
    SQLAlchemyRepository as PlayerSQLAlchemyRepository,
)
from src.rooms.application.service import RoomService
from src.rooms.domain.models import JoinRoomRequest, RoomCreationRequest, RoomID
from src.rooms.infrastructure.repository import WebSocketRepository as RoomWebSocketRepository

router = APIRouter()


@router.post("", status_code=201)
async def create_room(room_data: RoomCreationRequest, db_session: Session = Depends(get_db)) -> RoomID:
    service = RoomService(RoomWebSocketRepository(db_session), PlayerSQLAlchemyRepository(db_session))

    room = await service.create_room(room_data)
    return room


@router.put("/{roomID}/leave", status_code=200)
async def leave_room(roomID: int, playerID: PlayerID, db_session: Session = Depends(get_db)) -> None:
    service = RoomService(RoomWebSocketRepository(db_session), PlayerSQLAlchemyRepository(db_session))

    await service.leave_room(roomID, playerID.playerID)


@router.put("/{roomID}/join", status_code=200)
async def join_room(roomID: int, room_data: JoinRoomRequest, db_session: Session = Depends(get_db)) -> None:
    service = RoomService(RoomWebSocketRepository(db_session), PlayerSQLAlchemyRepository(db_session))

    await service.join_room(roomID, room_data.playerID, room_data.password)


@router.websocket("/{playerID}")
async def room_list_websocket(playerID: int, websocket: WebSocket, db_session: Session = Depends(get_db)):
    service = RoomService(RoomWebSocketRepository(db_session), PlayerSQLAlchemyRepository(db_session))

    try:
        await service.connect_to_room_list_websocket(playerID, websocket)
    except WebSocketDisconnect as e:
        await websocket.close(code=e.code, reason=e.reason)


@router.websocket("/{playerID}/{roomID}")
async def room_websocket(playerID: int, roomID: int, websocket: WebSocket, db_session: Session = Depends(get_db)):
    service = RoomService(RoomWebSocketRepository(db_session), PlayerSQLAlchemyRepository(db_session))

    try:
        await service.connect_to_room_websocket(playerID, roomID, websocket)
    except WebSocketDisconnect as e:
        await websocket.close(code=e.code, reason=e.reason)
