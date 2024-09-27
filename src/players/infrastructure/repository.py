from sqlalchemy.orm import Session
from typing import Union
from src.players.infrastructure.models import Player
from src.players.domain.models import PlayerResponse, PlayerUsername
from src.players.domain.repository import PlayerRepository


class SQLAlchemyRepository(PlayerRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, player: PlayerUsername) -> PlayerResponse:

        player_infra = Player(username=player.username)

        self.db.add(player_infra)
        self.db.commit()
        self.db.refresh(player_infra)

        return PlayerResponse(playerID=player_infra.playerID, username=player_infra.username)

    def find(self, playerID: int) -> Union[PlayerResponse, None]:

        player_infra = self.db.query(Player).filter(
            Player.playerID == playerID).first()

        if player_infra is None:
            return None

        return PlayerResponse(playerID=player_infra.playerID, username=player_infra.username)
