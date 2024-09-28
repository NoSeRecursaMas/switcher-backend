from sqlalchemy import Column, Integer, String, ForeignKey
from src.database import Base
from sqlalchemy.orm import relationship


class Lobby(Base):
    __tablename__ = 'lobbys'

    roomID = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    minPlayers = Column(Integer, nullable=True)
    maxPlayers = Column(Integer, nullable=True)
    password = Column(String, nullable=True)

    owner = Column(Integer, ForeignKey('players.playerID'))

    players = relationship(
        'Player', secondary='PlayerLobby', back_populates='lobbys')

    def __repr__(self):
        return f"<Lobby(name={self.name})>"


class PlayerLobby(Base):
    __tablename__ = 'PlayerLobby'

    playerID = Column(Integer, ForeignKey('players.playerID',
                      ondelete='CASCADE'), primary_key=True)
    roomID = Column(Integer, ForeignKey('lobbys.roomID',
                                        ondelete='CASCADE'), primary_key=True)
