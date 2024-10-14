from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Player(Base):
    __tablename__ = "players"

    playerID = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=True)

    rooms = relationship("Room", secondary="player_room", back_populates="players")
    cardsFigure = relationship("FigureCard", uselist=False, back_populates="player")
    movementCards = relationship("MovementCard", uselist=False, back_populates="player")

    def __repr__(self):
        return f"<Player(username={self.username})>"
