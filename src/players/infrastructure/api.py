from src.database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.players.application.service import PlayerService
from src.players.infrastructure.repository import SQLAlchemyRepository
from src.players.domain.models import PlayerCreationRequest, Player


router = APIRouter()


@router.post(path="", status_code=201)
def create_player(player_username: PlayerCreationRequest, db: Session = Depends(get_db)) -> Player:
    service = PlayerService(SQLAlchemyRepository(db))

    new_player = service.create_player(player_username)
    return new_player
