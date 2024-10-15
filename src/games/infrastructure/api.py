from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.database import get_db
from src.games.application.service import GameService
from src.games.domain.models import GameID
from src.games.infrastructure.repository import (
    WebSocketRepository as GameRepository,
)
from src.players.domain.models import PlayerID
from src.players.infrastructure.repository import SQLAlchemyRepository as PlayerRepository
from src.rooms.infrastructure.repository import WebSocketRepository as RoomRepository

router = APIRouter()


@router.post(path="/{roomID}", status_code=201)
async def start_game(roomID: int, playerID: PlayerID, db_session: Session = Depends(get_db)) -> GameID:
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)
    room_repository = RoomRepository(db_session)

    game_service = GameService(game_repository, player_repository, room_repository)

    gameID = await game_service.start_game(roomID, playerID)
    return gameID


@router.put(path="/{gameID}/turn", status_code=200)
async def skip_turn(gameID: int, playerID: PlayerID, db_session: Session = Depends(get_db)) -> None:
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)
    room_repository = RoomRepository(db_session)

    game_service = GameService(game_repository, player_repository, room_repository)
    await game_service.skip_turn(playerID.playerID, gameID)


@router.websocket("/{playerID}/{gameID}")
async def room_websocket(playerID: int, gameID: int, websocket: WebSocket, db_session: Session = Depends(get_db)):
    service = GameService(GameRepository(db_session), PlayerRepository(db_session))

    try:
        await service.connect_to_game_websocket(playerID, gameID, websocket)
    except WebSocketDisconnect as e:
        await websocket.close(code=e.code, reason=e.reason)


@router.put(path="/{gameID}/leave", status_code=200)
async def leave_game(gameID: int, playerID: PlayerID, db_session: Session = Depends(get_db)) -> None:
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)
    room_repository = RoomRepository(db_session)

    game_service = GameService(game_repository, player_repository, room_repository)

    await game_service.leave_game(gameID, playerID.playerID)
