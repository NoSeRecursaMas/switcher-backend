import json
from typing import List, Optional
from sqlalchemy.orm import Session

from src.games.domain.models import Game as GameDomain
from src.games.domain.models import GameCreationRequest, GameID
from src.games.infrastructure.models import Game, FigureCard
from src.games.domain.repository import GameRepository
from src.games.config import WHITE_CARDS_AMOUNT, BLUE_CARDS_AMOUNT
from src.rooms.infrastructure.repository import SQLAlchemyRepository as RoomRepository


class SQLAlchemyRepository(GameRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, roomID: int, new_board: list) -> GameID:
        board_json = json.dumps(new_board)
        last_movements = {}

        new_game = Game(
            board=board_json,
            lastMovements=last_movements,
            prohibitedColor=None,
            roomID=roomID
        )

        self.db_session.add(new_game)
        self.db_session.commit()
        self.db_session.refresh(new_game)

        return GameID(gameID=new_game.gameID)
    
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

    def is_player_in_game(self, gameID: int, playerID: int) -> bool:
        return True

    def create_figure_cards(self, roomID: int, gameID: int) -> None:

        room_repository = RoomRepository(self.db_session)

        players = room_repository.get_players(roomID)

        player_count = len(players)
        blue_amount = BLUE_CARDS_AMOUNT[player_count]
        white_amount = WHITE_CARDS_AMOUNT[player_count]
        card_count = 0
        for player in players:
            playable_count = 0
            for i in range(blue_amount):
                if playable_count <= 2:
                    playable = True
                    playable_count += 1
                else:
                    playable = False
                new_card = FigureCard(
                    type="blue",
                    cardID=card_count,
                    isPlayable=playable,
                    isBlocked=False,
                    playerID=player.playerID,
                    gameID=gameID.gameID
                )
                card_count += 1

                self.db_session.add(new_card)
                self.db_session.commit()
                self.db_session.refresh(new_card)
            for i in range(white_amount):
                if playable_count <= 2:
                    playable = True
                    playable_count += 1
                else:
                    playable = False
                new_card = FigureCard(
                    type="white",
                    cardID=card_count,
                    isPlayable=playable,
                    isBlocked=False,
                    playerID=player.playerID,
                    gameID=gameID.gameID
                )
                card_count += 1
                self.db_session.add(new_card)
                self.db_session.commit()
                self.db_session.refresh(new_card)
                
                


