from sqlalchemy import Column, Integer, String
from src.database import Base
from sqlalchemy.orm import relationship


class Player(Base):
    __tablename__ = 'Players'

    playerID = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=True)

    lobbys = relationship('Lobby', secondary='PlayerLobby',
                          back_populates='players')

    def __repr__(self):
        return f"<Player(username={self.username})>"
