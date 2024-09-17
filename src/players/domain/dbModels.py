from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Player(Base):
    __tablename__ = 'players'

    playerID = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=True)

    def __repr__(self):
        return f"<Player(username={self.username})>"
