import json
import random
from typing import List, Optional

from sqlalchemy.orm import Session

from src.games.config import (
    BLUE_CARDS,
    BLUE_CARDS_AMOUNT,
    MOVEMENT_CARDS,
    MOVEMENT_CARDS_AMOUNT,
    WHITE_CARDS,
    WHITE_CARDS_AMOUNT,
)
from src.games.domain.models import Game as GameDomain
from src.games.domain.models import GameCreationRequest, GameID
from src.games.domain.repository import GameRepository
from src.games.infrastructure.models import FigureCard, Game, MovementCard
from src.players.domain.models import Player
from src.rooms.infrastructure.models import Room

from src.rooms.infrastructure.repository import SQLAlchemyRepository as RoomRepository
from src.games.domain.models import Game as GameDomain
from src.games.domain.models import PlayerInfoPrivate, PlayerInfoPublic
from src.games.domain.models import FigureCard as FigureCardDomain
from src.games.domain.models import MovementCard as MovementCardDomain

class SQLAlchemyRepository(GameRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, roomID: int, new_board: list) -> GameID:
        board_json = json.dumps(new_board)
        last_movements = {}

        new_game = Game(board=board_json, lastMovements=last_movements, prohibitedColor=None, roomID=roomID)

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

    def get_game_players(self, gameID: int) -> List[Player]:
        room_repository = RoomRepository(self.db_session)
        roomID = self.db_session.query(Game).filter(Game.gameID == gameID).first().roomID
        return room_repository.get_players(roomID)

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

            playable_cards = random.sample(all_cards, 3)
            new_cards = []

            for card in all_cards:
                new_card = FigureCard(
                    type=card,
                    isPlayable=card in playable_cards,
                    isBlocked=False,
                    playerID=player.playerID,
                    gameID=gameID.gameID,
                )
                new_cards.append(new_card)

            self.db_session.add_all(new_cards)

        self.db_session.commit()

    def create_movement_cards(self, roomID: int, gameID: int) -> None:
        room_repository = RoomRepository(self.db_session)
        players = room_repository.get_players(roomID)
        player_count = len(players) - 2

        movement_cards_amount = MOVEMENT_CARDS_AMOUNT[player_count] * (player_count + 2) 
        movement_cards = MOVEMENT_CARDS * 7 
        all_movement_cards = random.sample(movement_cards, movement_cards_amount) 

        new_cards = []
        for card in all_movement_cards:
            new_card = MovementCard(type=card, playerID=None, gameID=gameID.gameID)
            new_cards.append(new_card)

        for index, player in enumerate(players):
            for i in range(3):
                new_cards[index * 3 + i].playerID = player.playerID

        self.db_session.add_all(new_cards)
        self.db_session.commit()

        

    def skip (self,gameID: int) -> None:
        game = self.db_session.query(Game).filter(Game.gameID == gameID).first()
        players = len(self.get_game_players(gameID))
        current_position = game.posEnabledToPlay

        current_player = self.db_session.query(Player) \
            .join(Room.players) \
            .join(Game, Room.roomID == Game.roomID) \
            .filter(Game.gameID == gameID, Player.position == current_position) \
            .first()
        
        if current_player:
            current_player.isActive = False

        min_players = (
             self.db_session.query(Room.minPlayers)
             .join(Game, Room.roomID == Game.roomID)
             .filter(Game.gameID == gameID)
             .first()
            )

        if current_position == players:
            game.posEnabledToPlay =  min_players
        else:
            game.posEnabledToPlay = current_position + 1

        next_player = self.db_session.query(Player)\
            .join(Room.players)\
            .join(Game, Room.roomID == Game.roomID)\
            .filter(Game.gameID == gameID, Player.position == game.posEnabledToPlay)\
            .first()
        
        if next_player:
            next_player.isActive = True
        
        self.db_session.commit()

    def replacement_movement_card(self, gameID: int, playerID: int) -> None:

        playable_cards = self.db_session.query(MovementCard).filter(
            MovementCard.gameID == gameID,
            MovementCard.playerID == playerID,
            MovementCard.isDiscarded == False,
            MovementCard.isPlayable == True
        ).all()        

        if len(playable_cards) < 3:
            available_cards = self.db_session.query(MovementCard).filter(
                MovementCard.gameID == gameID,
                MovementCard.isDiscarded == False,
                MovementCard.isPlayable == False
            ).limit(3 - len(playable_cards)).all()

            if len(available_cards) > 0:
                for card in available_cards:
                        card.isPlayable = True
                
        self.db_session.commit()

    def replacement_figure_card(self, gameID: int, playerID: int) -> None:
        figure_cards = self.db_session.query(FigureCard).filter(
            FigureCard.gameID == gameID,
            FigureCard.playerID == playerID,
        ).all()

        blocked_cards = [card for card in figure_cards if card.isBlocked]
 
        if len(blocked_cards) == 0:
            playable_cards = [card for card in figure_cards if card.isPlayable]
            available_cards = self.db_session.query(FigureCard).filter(
                FigureCard.gameID == gameID,
                FigureCard.playerID == playerID,
                FigureCard.isPlayable == False
            ).limit(3 - len(playable_cards)).all()

            if len(available_cards) > 0:
                for card in available_cards:
                    card.isPlayable = True
        self.db_session.commit()            
       

    def get_player_figure_cards(self, gameID:int, playerID:int) -> List[FigureCardDomain]:
        player_cards = self.db_session.query(FigureCard).filter(FigureCard.gameID == gameID, FigureCard.playerID == playerID).all()
        return [FigureCardDomain(type=card.type, isPlayable=card.isPlayable, isBlocked=card.isBlocked, cardID=card.cardID) for card in player_cards]
    
    def get_player_movement_cards(self, gameID:int, playerID:int) -> {MovementCardDomain}:
        player_cards = self.db_session.query(MovementCard).filter(MovementCard.gameID == gameID, MovementCard.playerID == playerID).all()
        return [MovementCardDomain(type=card.type, isDiscarded=card.isDiscarded, cardID=card.cardID) for card in player_cards]
    
    def get_player_private_info(self, gameID:int, playerID:int) -> PlayerInfoPrivate:
        movement_cards = self.get_player_movement_cards(gameID, playerID)
        return PlayerInfoPrivate(playerID=playerID, MovementCards=movement_cards)
    
    def get_player_public_info(self, gameID:int, playerID:int) -> PlayerInfoPublic:
        player = self.db_session.query(Player).filter(Player.playerID == playerID).first()
        figure_cards = self.get_player_figure_cards(gameID, playerID)
        return PlayerInfoPublic(playerID=playerID, username=player.username, 
                                position=player.position, isActive=player.isActive, 
                                sizeDeckFigure=len(figure_cards), FigureCards=figure_cards)
    
    def get_game_info(self, gameID:int) -> GameDomain:
        game = self.db_session.query(Game).filter(Game.gameID == gameID).first()
        players = self.get_game_players(gameID)
        player_info = [self.get_player_public_info(gameID, player.playerID) for player in players]
        return GameDomain(gameID=gameID, board=game.board, posEnabledToPlay=game.posEnabledToPlay, 
                          LastMovement=game.LastMovement, ProhibitedColor=game.ProhibitedColor, players=player_info)
