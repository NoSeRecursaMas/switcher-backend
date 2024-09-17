from sqlalchemy import Column, Integer, String
from src.database import Base


class Player(Base):
    __tablename__ = 'players'

    playerID = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=True)

    def __repr__(self):
        return f"<Player(username={self.username})>"
