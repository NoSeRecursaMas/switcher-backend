from src.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.players.application.service import PlayerService
from src.players.infrastructure.repository import SQLAlchemyRepository
from src.players.domain.models import PlayerUsername, PlayerResponse


router = APIRouter()


@router.post(path="", status_code=201)
def create_player(player_name: PlayerUsername, db: Session = Depends(get_db)) -> PlayerResponse:
    repository = SQLAlchemyRepository(db)
    service = PlayerService(repository)

    player = service.create_player(player_name)
    return player
