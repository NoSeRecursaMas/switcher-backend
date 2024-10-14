import json
import random
from typing import List, Optional

from fastapi.websockets import WebSocket
from sqlalchemy.orm import Session

from src.games.config import (
    BLUE_CARDS,
    BLUE_CARDS_AMOUNT,
    MOVEMENT_CARDS,
    MOVEMENT_CARDS_AMOUNT,
    WHITE_CARDS,
    WHITE_CARDS_AMOUNT,
)
from src.games.domain.models import FigureCard as FigureCardDomain
from src.games.domain.models import Game as GameDomain
from src.games.domain.models import GameID, PlayerInfoPrivate, PlayerInfoPublic
from src.games.domain.models import MovementCard as MovementCardDomain
from src.games.domain.repository import GameRepository, GameRepositoryWS
from src.games.infrastructure.models import FigureCard, Game, MovementCard
from src.games.infrastructure.websocket import MessageType, ws_manager_game
from src.players.domain.models import Player
from src.rooms.infrastructure.repository import SQLAlchemyRepository as RoomRepository


class SQLAlchemyRepository(GameRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, roomID: int, new_board: list) -> GameID:
        board_json = json.dumps(new_board)

        new_game = Game(board=board_json, lastMovements={}, prohibitedColor=None, roomID=roomID)

        self.db_session.add(new_game)
        self.db_session.commit()
        self.db_session.refresh(new_game)

        return GameID(gameID=new_game.gameID)

    def get(self, gameID: int) -> Optional[GameDomain]:
        game = self.db_session.get(Game, gameID)

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

    def get_players(self, gameID: int) -> List[Player]:
        room_repository = RoomRepository(self.db_session)
        game = self.db_session.get(Game, gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")
        roomID = game.roomID
        return room_repository.get_players(roomID)

    def is_player_in_game(self, playerID, gameID):
        players = self.get_players(gameID)
        return playerID in [player.playerID for player in players]

    def create_figure_cards(self, gameID: int) -> None:
        players = self.get_players(gameID)
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
                    gameID=gameID,
                )
                new_cards.append(new_card)

            self.db_session.add_all(new_cards)

        self.db_session.commit()

    def create_movement_cards(self, gameID: int) -> None:
        players = self.get_players(gameID)
        player_count = len(players) - 2

        movement_cards_amount = MOVEMENT_CARDS_AMOUNT[player_count] * (player_count + 2)
        movement_cards = MOVEMENT_CARDS * 7
        all_movement_cards = random.sample(movement_cards, movement_cards_amount)

        new_cards = []
        for card in all_movement_cards:
            new_card = MovementCard(type=card, playerID=None, gameID=gameID)
            new_cards.append(new_card)

        for index, player in enumerate(players):
            for i in range(3):
                new_cards[index * 3 + i].playerID = player.playerID

        self.db_session.add_all(new_cards)
        self.db_session.commit()

    def get_player_figure_cards(self, gameID: int, playerID: int) -> List[FigureCardDomain]:
        player_cards = (
            self.db_session.query(FigureCard).filter(FigureCard.gameID == gameID, FigureCard.playerID == playerID).all()
        )
        return [
            FigureCardDomain(type=card.type, isPlayable=card.isPlayable, isBlocked=card.isBlocked, cardID=card.cardID)
            for card in player_cards
        ]

    def get_player_movement_cards(self, gameID: int, playerID: int) -> List[MovementCardDomain]:
        player_cards = (
            self.db_session.query(MovementCard)
            .filter(MovementCard.gameID == gameID, MovementCard.playerID == playerID)
            .all()
        )
        return [
            MovementCardDomain(type=card.type, isDiscarded=card.isDiscarded, cardID=card.cardID)
            for card in player_cards
        ]

    def get_player_private_info(self, gameID: int, playerID: int) -> PlayerInfoPrivate:
        movement_cards = self.get_player_movement_cards(gameID, playerID)
        return PlayerInfoPrivate(playerID=playerID, MovementCards=movement_cards)

    def get_player_public_info(self, gameID: int, playerID: int) -> PlayerInfoPublic:
        player = self.db_session.query(Player).filter(Player.playerID == playerID).first()
        figure_cards = self.get_player_figure_cards(gameID, playerID)
        return PlayerInfoPublic(
            playerID=playerID,
            username=player.username,
            position=player.position,
            isActive=player.isActive,
            sizeDeckFigure=len(figure_cards),
            FigureCards=figure_cards,
        )

    def get_game_info(self, gameID: int) -> GameDomain:
        game = self.db_session.query(Game).filter(Game.gameID == gameID).first()
        players = self.get_players(gameID)
        player_info = [self.get_player_public_info(gameID, player.playerID) for player in players]
        return GameDomain(
            gameID=gameID,
            board=game.board,
            posEnabledToPlay=game.posEnabledToPlay,
            LastMovement=game.LastMovement,
            ProhibitedColor=game.ProhibitedColor,
            players=player_info,
        )


class WebSocketRepository(GameRepositoryWS, SQLAlchemyRepository):
    async def setup_connection_game(self, playerID: int, gameID: int, websocket: WebSocket) -> None:
        """Establece la conexión con el websocket de un juego
        y le envia el estado actual de la sala

        Args:
            playerID (int): ID del jugador
            gameID (int): ID del juego
            websocket (WebSocket): Conexión con el cliente
        """
        await ws_manager_game.connect(playerID, gameID, websocket)
        game = self.get_game_info(gameID)
        game_json = game.model_dump()
        await ws_manager_game.send_personal_message(MessageType.STATUS, game_json, websocket)
        await ws_manager_game.keep_listening(websocket)

    async def broadcast_status_game(self, gameID: int) -> None:
        pass
