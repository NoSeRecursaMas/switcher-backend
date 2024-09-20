from fastapi import APIRouter, Depends
from src.lobbys.domain.models import LobbyResponse, CreteLobbyRequest
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("", status_code=201)
def create_lobby(lobby_data: CreteLobbyRequest, db: Session = Depends(get_db)) -> LobbyResponse:
    repository = SQLAlchemyRepository(db)
    service = LobbyService(repository)
