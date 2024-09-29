from sqlalchemy.orm import Session
from typing import Union
from src.players.infrastructure.models import Player as PlayerDB
from src.players.domain.models import Player, PlayerCreationRequest
from src.players.domain.repository import PlayerRepository


class SQLAlchemyRepository(PlayerRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, player: PlayerCreationRequest) -> Player:

        player = PlayerDB(username=player.username)

        self.db.add(player)
        self.db.commit()
        self.db.refresh(player)

        return Player(playerID=player.playerID, username=player.username)

    def get(self, playerID: int) -> Union[Player, None]:
        player = self.db.query(PlayerDB).filter(
            PlayerDB.playerID == playerID).first()

        if player is None:
            return None

        return Player(playerID=player.playerID, username=player.username)

    def update(self, player: Player) -> None:
        self.db.query(PlayerDB).filter(
            PlayerDB.playerID == player.playerID).update({"username": player.username})
        self.db.commit()

    def delete(self, playerID: int) -> None:
        self.db.query(PlayerDB).filter(
            PlayerDB.playerID == playerID).delete()
        self.db.commit()
