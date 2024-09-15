from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, nullable = True, unique = True)

    def __repr__(self):
        return f"<Player(name={self.name})>"