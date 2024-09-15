from src.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.players.application.service import PlayerService
from src.players.infrastructure.repository import SQLAlchemyPlayerRepository

 
 
router = APIRouter()

@router.post(path = "", status_code=201)
def create_player(player_name: str, db: Session = Depends(get_db)):
    try:
       
        player_repository = SQLAlchemyPlayerRepository(db)
        player_service = PlayerService(player_repository)
        
        
        
        player = player_service.create_player_use_case(player_name)
        
        
        return {"id": player.id, "name": player.name}

    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e)) 

