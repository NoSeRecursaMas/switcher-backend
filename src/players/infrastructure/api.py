from src.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.players.application.service import PlayerService
from src.players.infrastructure.repository import SQLAlchemyRepository
from src.players.domain.epModels import PlayerUsername, PlayerResponse


router = APIRouter()
# localhost:8000/players?username=pedro


@router.post(path="", status_code=201)
def create_player(player_name: PlayerUsername, db: Session = Depends(get_db)) -> PlayerResponse:
    try:

        repository = SQLAlchemyRepository(db)
        service = PlayerService(repository)

        player = service.create_player(player_name.username)

        return player

    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
