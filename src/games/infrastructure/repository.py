from typing import List, Optional
from sqlalchemy.orm import Session

from src.games.domain.models import Game as GameDomain
from src.games.domain.models import GameCreationRequest, GameID
from src.games.infrastructure.models import Game
from src.games.domain.repository import GameRepository

class SQLAlchemyRepository(GameRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, game: GameCreationRequest) -> GameID:
        game = Game(
            board=game.board,
            lastMovements=game.lastMovements,
            prohibitedColor=game.prohibitedColor,
        )

        self.db_session.add(game)
        self.db_session.commit()
        self.db_session.refresh(game)

        return GameID(gameID=game.gameID)
    
    def get(self, gameID: int) -> Optional[GameDomain]:
        game = self.db_session.query(Game).filter(Game.gameID == gameID).first()

        if game is None:
            return None

        return GameDomain(
            gameID=game.gameID,
            board=game.board,
            lastMovements=game.lastMovements,
            prohibitedColor=game.prohibitedColor,
        )
    
    def delete(self, gameID: int) -> None:
        game = self.db_session.query(Game).filter(Game.gameID == gameID).first()
        self.db_session.delete(game)
        self.db_session.commit()

    def associate_player_from_game(self, gameID: int, playerID: int) -> None:
        pass

    def disassociate_player_from_game(self, gameID: int, playerID: int) -> None:
        pass