from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class Lobby(Base):
    __tablename__ = 'lobbys'

    lobbyID = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    min_players = Column(Integer, nullable=True)
    max_players = Column(Integer, nullable=True)
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
    lobbyID = Column(Integer, ForeignKey('lobbys.lobbyID',
                     ondelete='CASCADE'), primary_key=True)
