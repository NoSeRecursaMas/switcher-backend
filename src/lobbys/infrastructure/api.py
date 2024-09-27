from src.database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.lobbys.application.service import LobbyService
from src.players.infrastructure.repository import SQLAlchemyRepository as PlayerSQLAlchemyRepository
from src.lobbys.infrastructure.repository import SQLAlchemyRepository as LobbySQLAlchemyRepository
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest
from src.players.domain.models import PlayerID

router = APIRouter()


@router.post("", status_code=201)
def create_lobby(lobby_data: CreateLobbyRequest, db: Session = Depends(get_db)) -> LobbyResponse:
    lobby_repository = LobbySQLAlchemyRepository(db)
    player_repository = PlayerSQLAlchemyRepository(db)
    service = LobbyService(lobby_repository, player_repository)

    lobby = service.create_lobby(lobby_data)
    return lobby


@router.get("/{lobby_id}/leave", status_code=200)
def leave_lobby(lobby_id: int, player_id: PlayerID, db: Session = Depends(get_db)) -> None:
    lobby_repository = LobbySQLAlchemyRepository(db)
    player_repository = PlayerSQLAlchemyRepository(db)
    service = LobbyService(lobby_repository, player_repository)

    service.leave_lobby(lobby_id, player_id)

    return None
