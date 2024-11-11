from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.database import get_db
from src.games.application.service import GameService
from src.games.domain.models import BlockCardRequest, FigureCardRequest, GameID, MovementCardRequest
from src.games.infrastructure.repository import (
    WebSocketRepository as GameRepository,
)
from src.players.domain.models import PlayerID
from src.players.infrastructure.repository import SQLAlchemyRepository as PlayerRepository
from src.rooms.infrastructure.repository import WebSocketRepository as RoomRepository

router = APIRouter()


@router.post(path="/{roomID}", status_code=201)
async def start_game(
    roomID: int, playerID: PlayerID, background_tasks: BackgroundTasks, db_session: Session = Depends(get_db)
) -> GameID:
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)
    room_repository = RoomRepository(db_session)

    game_service = GameService(game_repository, player_repository, room_repository)

    gameID = await game_service.start_game(roomID, playerID, background_tasks)
    return gameID


@router.put(path="/{gameID}/turn", status_code=200)
async def skip_turn(
    gameID: int, playerID: PlayerID, background_tasks: BackgroundTasks, db_session: Session = Depends(get_db)
) -> None:
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)
    room_repository = RoomRepository(db_session)

    game_service = GameService(game_repository, player_repository, room_repository)
    await game_service.skip_turn(playerID.playerID, gameID, background_tasks)


@router.websocket("/{playerID}/{gameID}")
async def room_websocket(playerID: int, gameID: int, websocket: WebSocket, db_session: Session = Depends(get_db)):
    service = GameService(GameRepository(db_session), PlayerRepository(db_session))

    try:
        await service.connect_to_game_websocket(playerID, gameID, websocket)
    except WebSocketDisconnect as e:
        await websocket.close(code=e.code, reason=e.reason)


@router.post("/{gameID}/movement", status_code=201)
async def play_movement_card(gameID: int, request: MovementCardRequest, db_session: Session = Depends(get_db)):
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)

    game_service = GameService(game_repository, player_repository)

    await game_service.play_movement_card(gameID, request)


@router.put(path="/{gameID}/leave", status_code=200)
async def leave_game(gameID: int, playerID: PlayerID, db_session: Session = Depends(get_db)) -> None:
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)
    room_repository = RoomRepository(db_session)

    game_service = GameService(game_repository, player_repository, room_repository)

    await game_service.leave_game(gameID, playerID.playerID)


@router.delete(path="/{gameID}/movement", status_code=200)
async def delete_partial_movement(gameID: int, playerID: int, db_session: Session = Depends(get_db)) -> None:
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)
    game_service = GameService(game_repository, player_repository)
    await game_service.delete_partial_movement(gameID, playerID)


@router.post(path="/{gameID}/figure", status_code=201)
async def play_figure(
    gameID: int,
    request: FigureCardRequest,
    db_session: Session = Depends(get_db),
) -> None:
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)
    room_repository = RoomRepository(db_session)

    game_service = GameService(game_repository, player_repository, room_repository)

    await game_service.play_figure(gameID, request.playerID, request.cardID, request.figure)


@router.put(path="/{gameID}/block", status_code=201)
async def block_figure(
    gameID: int,
    request: BlockCardRequest,
    db_session: Session = Depends(get_db),
) -> None:
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)
    room_repository = RoomRepository(db_session)

    game_service = GameService(game_repository, player_repository, room_repository)

    await game_service.block_figure(gameID, request.playerID, request.targetID, request.cardID, request.figure)
