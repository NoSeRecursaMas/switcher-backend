from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Game(Base):
    __tablename__ = "games"

    gameID = Column(Integer, primary_key=True)
    roomID = Column(ForeignKey("rooms.roomID"), nullable=False, unique=True)
    board = Column(JSON)
    lastMovements = Column(JSON, nullable=True)
    prohibitedColor = Column(String, nullable=True)
    room = relationship("Room", back_populates="game")
    posEnabledToPlay = Column(Integer, default=1)
    timestamp_next_turn = Column(DateTime, nullable=True)

    figureDeck = relationship("FigureCard", back_populates="game")
    movementDeck = relationship("MovementCard", back_populates="game")

    def __repr__(self):
        return f"<Game(gameID={self.gameID}, board={self.board}, lastMovements={self.lastMovements}, prohibitedColor={self.prohibitedColor}, roomID={self.roomID})>"


class FigureCard(Base):
    __tablename__ = "figure_cards"

    cardID = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=True)
    isBlocked = Column(Boolean, default=False)
    isPlayable = Column(Boolean, default=False)
    wasBlocked = Column(Boolean, default=False)

    playerID = Column(ForeignKey("players.playerID"), nullable=False)
    gameID = Column(ForeignKey("games.gameID"), nullable=False)

    player = relationship("Player", back_populates="cardsFigure")
    game = relationship("Game", back_populates="figureDeck")

    def __repr__(self):
        return f"<FigureCard(cardID={self.cardID}, type={self.type}, isBlocked={self.isBlocked})>"


class MovementCard(Base):
    __tablename__ = "movement_cards"

    cardID = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=True)
    isDiscarded = Column(Boolean, default=False)

    playerID = Column(ForeignKey("players.playerID"), nullable=True)
    gameID = Column(ForeignKey("games.gameID"), nullable=False)

    player = relationship("Player", back_populates="movementCards")
    game = relationship("Game", back_populates="movementDeck")

    def __repr__(self):
        return f"<MovementCard(cardID={self.cardID}, type={self.type}, isDiscarded={self.isDiscarded})>"
