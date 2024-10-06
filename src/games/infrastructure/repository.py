from typing import List, Optional, NULL
from sqlalchemy.orm import Session

from src.games.domain.models import Game as GameDomain
from src.games.domain.models import GameCreationRequest, GameID
from src.games.infrastructure.models import Game
from src.games.domain.repository import GameRepository

class SQLAlchemyRepository(GameRepository):
    def __init__(self, room_repository: SQLAlchemyRepository, db_session: Session):
        self.db_session = db_session
        self.room_repository = room_repository

    def create(self, game: GameCreationRequest) -> GameID:
        board_json = game.board.json.dumps()
        last_movements = {}

        game = Game(
            board=board_json,
            lastMovements=last_movements,
            prohibitedColor=NULL,
            roomID=game.roomID
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

    def create_figure_cards(self, roomID: int, gameID: int) -> None:
        
        players = self.room_repository.get_players(roomID)

        player_count = len(players)

        for player in players:
            for i in player_count
                


