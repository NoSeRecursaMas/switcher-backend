from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Boolean
from sqlalchemy.orm import relationship
from src.database import Base

class Game(Base):
    __tablename__ = "games"

    gameID = Column(Integer, primary_key=True)
    board = Column(JSON)
    lastMovements = Column(JSON, nullable=True)
    prohibitedColor = Column(String, nullable=True)

    roomID = Column(ForeignKey("rooms.roomID"), nullable=False)

    room = relationship("Room", back_populates="rooms")

    def __repr__(self):
        return f"<Game(gameID={self.gameID}, board={self.board}, lastMovements={self.lastMovements}, prohibitedColor={self.prohibitedColor}, roomID={self.roomID})>"

class FigureCard(Base):
    __tablename__ = "figure_cards"

    cardID = Column(Integer, primary_key=True)
    type = Column(String, nullable=True)
    isBlocked = Column(Boolean, default=False)
    isPlayable = Column(Boolean, default=False)

    playerID = Column(ForeignKey("player.playerID"), nullable=False)
    gameID = Column(ForeignKey("game.gameID"), nullable=False)

    player = relationship("PlayerFigureCard", back_populates="players")
    game = relationship("GameFigureDeck", back_populates="games")

    def __repr__(self):
        return f"<FigureCard(cardID={self.cardID}, type={self.type}, isBlocked={self.isBlocked})>"

class MovementCard(Base):
    __tablename__ = "movement_cards"

    cardID = Column(Integer, primary_key=True)
    type = Column(String, nullable=True)
    isPlayable = Column(Boolean, default=False)
    isDiscarded = Column(Boolean, default=False)
    
    playerID = Column(ForeignKey("player.playerID"), nullable=True)
    gameID = Column(ForeignKey("game.gameID"), nullable=False)

    player = relationship("PlayerMovementDeck", back_populates="players")
    game = relationship("GameMovementDeck", back_populates="games")


    def __repr__(self):
        return f"<MovementCard(cardID={self.cardID}, type={self.type}, isDiscarded={self.isDiscarded})>"
    
    


