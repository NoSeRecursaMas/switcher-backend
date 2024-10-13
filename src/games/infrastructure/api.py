from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.players.domain.models import PlayerID
from src.games.domain.models import GameID
from src.games.application.service import GameService
from src.games.infrastructure.repository import SQLAlchemyRepository as GameRepository
from src.rooms.infrastructure.repository import SQLAlchemyRepository as RoomRepository
from src.players.infrastructure.repository import SQLAlchemyRepository as PlayerRepository
router = APIRouter()


@router.post(path="/{roomID}", status_code=201)
def start_game(roomID: int, playerID : PlayerID, db_session: Session = Depends(get_db)) -> GameID:
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)

    game_service = GameService(game_repository, player_repository)
    gameID = game_service.start_game(roomID, playerID)
    return gameID
    
@router.put(path="/{gameID}/turn", status_code=200)
def skip_turn(gameID: int,playerID : PlayerID, db_session: Session = Depends(get_db)) -> None:
    game_repository = GameRepository(db_session)
    player_repository = PlayerRepository(db_session)

    game_service = GameService(game_repository,player_repository)
    game_service.skip_turn(playerID,gameID)