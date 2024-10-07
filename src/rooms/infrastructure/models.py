from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Room(Base):
    __tablename__ = "rooms"

    roomID = Column(Integer, primary_key=True, index=True)
    roomName = Column(String, nullable=True)
    minPlayers = Column(Integer, nullable=True)
    maxPlayers = Column(Integer, nullable=True)
    password = Column(String, nullable=True)

    hostID = Column(Integer, ForeignKey("players.playerID"))

    players = relationship("Player", secondary="player_room", back_populates="rooms")

    def __repr__(self):
        return f"<Room(roomName={self.roomName})>"


class PlayerRoom(Base):
    __tablename__ = "player_room"

    playerID = Column(Integer, ForeignKey("players.playerID", ondelete="CASCADE"), primary_key=True)
    roomID = Column(Integer, ForeignKey("rooms.roomID", ondelete="CASCADE"), primary_key=True)
