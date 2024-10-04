from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Boolean
from sqlalchemy.orm import relationship
from src.database import Base

class Game(Base):
    __tablename__ = "games"

    gameID = Column(Integer, primary_key=True, index=True)
    board = Column(JSON)
    lastMovements = Column(JSON, nullable=True)
    prohibitedColor = Column(String, nullable=True)

    players = relationship("PlayerGame", back_populates="games")

    def __repr__(self):
        return f"<Game(gameID={self.gameID}, board={self.board}, lastMovements={self.lastMovements}, prohibitedColor={self.prohibitedColor})>"
   
class PlayerGame(Base):
    __tablename__ = "player_game"

    playerID = Column(Integer, ForeignKey("players.playerID"), primary_key=True)
    gameID = Column(Integer, ForeignKey("games.gameID"), primary_key=True)
    position = Column(Integer, nullable=True)
    isActive = Column(Boolean, nullable=True)
    sizeDeckFigure = Column(Integer, nullable=True)

    game = relationship("Game", back_populates="players")
    player = relationship("Player", back_populates="games")
    figureCards = relationship("FigureCard", back_populates="playerGame")
    movementCards = relationship("MovementCard", back_populates="playerGame")
    
    def __repr__(self):
        return f"<PlayerGame(playerID={self.playerID}, gameID={self.gameID})>"
    
class FigureCard(Base):
    __tablename__ = "figure_cards"

    cardID = Column(Integer, primary_key=True)
    type = Column(String, nullable=True)
    isBlocked = Column(Boolean, nullable=True)
    playerGameID = Column(Integer, ForeignKey("player_game.playerID"))

    playerGame = relationship("PlayerGame", back_populates="figureCards")

    def __repr__(self):
        return f"<FigureCard(cardID={self.cardID}, type={self.type}, isBlocked={self.isBlocked})>"


class MovementCard(Base):
    __tablename__ = "movement_cards"

    cardID = Column(Integer, primary_key=True)
    type = Column(String, nullable=True)
    isDiscarded = Column(Boolean, nullable=True)
    playerGameID = Column(Integer, ForeignKey("player_game.playerID"))

    playerGame = relationship("PlayerGame", back_populates="movementCards")

    def __repr__(self):
        return f"<MovementCard(cardID={self.cardID}, type={self.type}, isDiscarded={self.isDiscarded})>"
    
    


