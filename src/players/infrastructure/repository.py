from sqlalchemy.orm import Session
from src.players.domain.model import Player
from src.players.domain.repository import PlayerRepository

class SQLAlchemyPlayerRepository(PlayerRepository):
    def __init__(self, db: Session):
        
        self.db = db

    def save(self, player: Player):
        
        self.db.add(player)
        self.db.commit()

        return player