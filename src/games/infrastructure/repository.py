import json
import random
from typing import List, Optional
from sqlalchemy.orm import Session

from src.games.domain.models import Game as GameDomain
from src.games.domain.models import GameCreationRequest, GameID
from src.games.infrastructure.models import Game, FigureCard, MovementCard
from src.games.domain.repository import GameRepository
from src.games.config import WHITE_CARDS_AMOUNT, BLUE_CARDS_AMOUNT, WHITE_CARDS, BLUE_CARDS, MOVEMENT_CARDS_AMOUNT, MOVEMENT_CARDS
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
        game = self.db_session.query(Game).filter(
            Game.gameID == gameID).first()

        if game is None:
            return None

        return GameDomain(
            gameID=game.gameID,
            board=game.board,
            lastMovements=game.lastMovements,
            prohibitedColor=game.prohibitedColor,
        )

    def delete(self, gameID: int) -> None:
        game = self.db_session.query(Game).filter(
            Game.gameID == gameID).first()
        self.db_session.delete(game)
        self.db_session.commit()

    def is_player_in_game(self, gameID: int, playerID: int) -> bool:
        return True

    def create_figure_cards(self, roomID: int, gameID: int) -> None:

        room_repository = RoomRepository(self.db_session)
        players = room_repository.get_players(roomID)
        player_count = len(players) - 2

        blue_amount = BLUE_CARDS_AMOUNT[player_count]
        white_amount = WHITE_CARDS_AMOUNT[player_count]

        blue_cards = BLUE_CARDS * 2
        white_cards = WHITE_CARDS * 2

        for player in players:
            slected_blue_cards = random.sample(blue_cards, blue_amount)
            slected_white_cards = random.sample(white_cards, white_amount)

            all_cards = slected_blue_cards + slected_white_cards

            playable_cards = random.sample(all_cards,3)
            playable_count = 0
            new_cards = []

            for card in all_cards:
                playable = card in playable_cards
                if playable:
                    playable_count += 1
                if playable_count > 3:
                    playable = False

                new_card = FigureCard(
                    type=card,
                    isPlayable=playable,
                    isBlocked=False,
                    playerID=player.playerID,
                    gameID=gameID.gameID
                )
                new_cards.append(new_card)

            self.db_session.add_all(new_cards)

        self.db_session.commit()

    def create_movement_cards(self, roomID: int, gameID: int) -> None:
        room_repository = RoomRepository(self.db_session)
        players = room_repository.get_players(roomID)
        player_count = len(players) - 2

        movement_cards_amount = MOVEMENT_CARDS_AMOUNT[player_count]
        movement_cards = MOVEMENT_CARDS * 7
        all_movement_cards = random.sample(movement_cards, movement_cards_amount)
        playable_cards = random.sample(all_movement_cards, 3)
        
        for player in players:
            new_cards = []
            playable_count = 0
            for card in all_movement_cards:
                playable = card in playable_cards
                if playable:
                    playable_count += 1
                if playable_count > 3:
                    playable = False
                new_card = MovementCard(
                    type=card,
                    isPlayable=playable,
                    isDiscarded=False,
                    playerID=player.playerID,
                    gameID=gameID.gameID
                )
                new_cards.append(new_card)

            self.db_session.add_all(new_cards)
        self.db_session.commit()