from sqlalchemy import Column, Integer, String, ForeingKey
from src.database import Base


class Lobby(Base):
    __tablename__ = 'lobbys'

    lobbyID = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    min_players = Column(Integer, nullable=True)
    max_players = Column(Integer, nullable=True)
    password = Column(String, nullable=True)

    host = Column(Integer, ForeingKey('players.playerID'))

    def __repr__(self):
        return f"<Lobby(name={self.name})>"
