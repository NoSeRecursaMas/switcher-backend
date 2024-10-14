from typing import Optional

from sqlalchemy.orm import Session

from src.players.domain.models import Player, PlayerCreationRequest
from src.players.domain.repository import PlayerRepository
from src.players.infrastructure.models import Player as PlayerDB


class SQLAlchemyRepository(PlayerRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, player_data: PlayerCreationRequest) -> Player:
        new_player = PlayerDB(username=player_data.username)

        self.db_session.add(new_player)
        self.db_session.commit()
        self.db_session.refresh(new_player)

        return Player(playerID=new_player.playerID, username=new_player.username)

    def get(self, playerID: int) -> Optional[Player]:
        player = self.db_session.get(PlayerDB, playerID)

        if player is None:
            return None

        return Player(playerID=player.playerID, username=player.username)

    def update(self, player: Player) -> None:
        self.db_session.query(PlayerDB).filter(PlayerDB.playerID == player.playerID).update(
            {"username": player.username}
        )
        self.db_session.commit()

    def delete(self, playerID: int) -> None:
        self.db_session.query(PlayerDB).filter(PlayerDB.playerID == playerID).delete()
        self.db_session.commit()
