from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class Room(Base):
    __tablename__ = 'Rooms'

    roomID = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    minPlayers = Column(Integer, nullable=True)
    maxPlayers = Column(Integer, nullable=True)
    password = Column(String, nullable=True)

    hostID = Column(Integer, ForeignKey('Players.playerID'))

    players = relationship(
        'Player', secondary='PlayerRoom', back_populates='Rooms')

    def __repr__(self):
        return f"<Room(name={self.name})>"


class PlayerRoom(Base):
    __tablename__ = 'PlayerRoom'

    playerID = Column(Integer, ForeignKey('Players.playerID',
                      ondelete='CASCADE'), primary_key=True)
    roomID = Column(Integer, ForeignKey('Rooms.roomID',
                                        ondelete='CASCADE'), primary_key=True)
