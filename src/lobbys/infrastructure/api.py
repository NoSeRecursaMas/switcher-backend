from src.database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.lobbys.application.service import LobbyService
from src.players.infrastructure.repository import SQLAlchemyRepository as PlayerSQLAlchemyRepository
from src.lobbys.infrastructure.repository import SQLAlchemyRepository as LobbySQLAlchemyRepository
from src.lobbys.domain.models import LobbyResponse, CreateLobbyRequest, GetLobbyResponse, GetLobbyData
from src.players.domain.models import PlayerID

router = APIRouter()


@router.post("", status_code=201)
def create_lobby(lobby_data: CreateLobbyRequest, db: Session = Depends(get_db)) -> LobbyResponse:
    lobby_repository = LobbySQLAlchemyRepository(db)
    player_repository = PlayerSQLAlchemyRepository(db)
    service = LobbyService(lobby_repository, player_repository)

    lobby = service.create_lobby(lobby_data)
    return lobby


@router.get("", status_code=200)
def get_lobby(db: Session = Depends(get_db)) -> list[GetLobbyResponse]:

    lobby_repository = LobbySQLAlchemyRepository(db)
    service = LobbyService(lobby_repository)

    lobby_all = service.get_lobby()

    return lobby_all

  
@router.get("/{lobby_id}",status_code=200)
def get_data_lobby(lobby_id, db: Session = Depends(get_db)) -> GetLobbyData:

    lobby_repository = LobbySQLAlchemyRepository(db)
    service = LobbyService(lobby_repository)

    lobby_data = service.get_data_lobby(lobby_id)

    return lobby_data

@router.put("/{lobby_id}/join", status_code=200)
def join_lobby(lobby_id:int, player_id: PlayerID, db: Session = Depends(get_db)) -> LobbyResponse:

    lobby_repository = LobbySQLAlchemyRepository(db)
    player_repository = PlayerSQLAlchemyRepository(db)
    service = LobbyService(lobby_repository, player_repository)

    service.join_lobby(lobby_id, player_id.playerID)

    return None