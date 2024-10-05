from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.players.domain.models import PlayerID
from src.games.domain.models import GameID
from src.games.application.service import GameService

router = APIRouter()


@router.post(path="/{roomID}", status_code=201)
def start_game(roomID: int, playerID : PlayerID, db_session: Session = Depends(get_db)) -> GameID:
    
    pass

