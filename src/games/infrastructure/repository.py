import json
import random
from typing import List, Optional, Tuple

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
from src.games.domain.models import (
    BoardPiece,
    FigureCard,
    Game,
    GameID,
    GamePublicInfo,
    MovementCard,
    PlayerPublicInfo,
    Winner,
)
from src.games.domain.repository import GameRepository, GameRepositoryWS
from src.games.infrastructure.models import FigureCard as FigureCardDB
from src.games.infrastructure.models import Game as GameDB
from src.games.infrastructure.models import MovementCard as MovementCardDB
from src.games.infrastructure.websocket import MessageType, ws_manager_game
from src.players.infrastructure.models import Player as PlayerDB
from src.rooms.infrastructure.models import PlayerRoom as PlayerRoomDB
from src.rooms.infrastructure.repository import SQLAlchemyRepository as RoomRepository


class SQLAlchemyRepository(GameRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, roomID: int, new_board: list) -> GameID:
        board_json = json.dumps(new_board)

        new_game = GameDB(board=board_json, lastMovements={}, prohibitedColor=None, roomID=roomID)

        self.db_session.add(new_game)
        self.db_session.commit()
        self.db_session.refresh(new_game)

        return GameID(gameID=new_game.gameID)

    def create_figure_cards(self, gameID: int) -> None:
        players = self.get_players(gameID)
        amount_players_index = len(players) - 2

        blue_amount = BLUE_CARDS_AMOUNT[amount_players_index]
        white_amount = WHITE_CARDS_AMOUNT[amount_players_index]

        all_blue_cards = BLUE_CARDS * 2
        all_white_cards = WHITE_CARDS * 2
        selected_blue_cards = random.sample(all_blue_cards, blue_amount)
        selected_white_cards = random.sample(all_white_cards, white_amount)
        selected_cards = selected_blue_cards + selected_white_cards
        random.shuffle(selected_cards)
        amount_per_player = len(selected_cards) // len(players)

        new_cards: List[FigureCardDB] = []

        for i, player in enumerate(players):
            for j in range(amount_per_player):
                new_card = FigureCardDB(
                    type=selected_cards[j + i * amount_per_player],
                    isPlayable=j < 3,
                    isBlocked=False,
                    playerID=player.playerID,
                    gameID=gameID,
                )
                new_cards.append(new_card)

        self.db_session.add_all(new_cards)
        self.db_session.commit()

    def create_movement_cards(self, gameID: int) -> None:
        players = self.get_players(gameID)

        movement_cards_amount = MOVEMENT_CARDS_AMOUNT[len(players) - 2] * len(players)
        all_movement_cards = MOVEMENT_CARDS * 7
        selected_movement_cards = random.sample(all_movement_cards, movement_cards_amount)

        new_cards: List[MovementCardDB] = []
        for card in selected_movement_cards:
            new_card = MovementCardDB(type=card, playerID=None, gameID=gameID)
            new_cards.append(new_card)

        for index, player in enumerate(players):
            for i in range(3):
                new_cards[index * 3 + i].playerID = player.playerID

        self.db_session.add_all(new_cards)
        self.db_session.commit()

    def delete(self, gameID: int) -> None:
        game = self.db_session.get(GameDB, gameID)
        self.db_session.delete(game)
        self.db_session.commit()

    def get(self, gameID: int) -> Optional[Game]:
        game = self.db_session.get(GameDB, gameID)

        if game is None:
            return None

        room_repository = RoomRepository(self.db_session)
        room_repository.get_players(game.roomID)
        return Game(
            gameID=game.gameID,
            board=self.get_board(gameID),
            prohibitedColor=game.prohibitedColor,
            posEnabledToPlay=game.posEnabledToPlay,
            players=self.get_players(gameID),
        )

    def get_board(self, gameID: int) -> List[BoardPiece]:
        game = self.db_session.get(GameDB, gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")
        board_json = json.loads(game.board)
        board: List[BoardPiece] = []
        for piece_db in board_json:
            is_partial = self.is_piece_partial(gameID, piece_db["posX"], piece_db["posY"])
            piece = BoardPiece(
                posX=piece_db["posX"], posY=piece_db["posY"], color=piece_db["color"], isPartial=is_partial
            )
            board.append(piece)
        return board

    def is_piece_partial(self, gameID: int, posX: int, posY: int) -> bool:
        # IMPLEMENTAR ESTO EN EL TICKET DE MOVIMIENTOS PARCIALES
        # IMPLEMENTAR ESTO EN EL TICKET DE MOVIMIENTOS PARCIALES
        # IMPLEMENTAR ESTO EN EL TICKET DE MOVIMIENTOS PARCIALES
        return False

    def get_players(self, gameID: int) -> List[PlayerPublicInfo]:
        game = self.db_session.get(GameDB, gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")
        roomID = game.roomID

        db_players = self.db_session.query(PlayerRoomDB).filter(PlayerRoomDB.roomID == roomID).all()
        players = []

        for player in db_players:
            username = self.db_session.get(PlayerDB, player.playerID).username
            amount_non_playable, playable_cards_figure = self.get_player_figure_cards(gameID, player.playerID)

            players.append(
                PlayerPublicInfo(
                    playerID=player.playerID,
                    username=username,
                    position=player.position,
                    isActive=player.isActive,
                    sizeDeckFigure=amount_non_playable,
                    cardsFigure=playable_cards_figure,
                )
            )
        return players

    def get_player_figure_cards(self, gameID: int, playerID: int) -> Tuple[int, List[FigureCard]]:
        figure_cards = self.db_session.query(FigureCardDB).filter(
            FigureCardDB.gameID == gameID, FigureCardDB.playerID == playerID
        )
        amount_non_playable = figure_cards.filter(not FigureCardDB.isPlayable).count()

        playable_cards: List[FigureCard] = []
        for card in figure_cards:
            if card.isPlayable:
                playable_cards.append(FigureCard(type=card.type, cardID=card.cardID, isBlocked=card.isBlocked))

        return amount_non_playable, playable_cards

    def get_player_movement_cards(self, gameID: int, playerID: int) -> List[MovementCard]:
        cards_db = self.db_session.query(MovementCardDB).filter(
            MovementCardDB.gameID == gameID, MovementCardDB.playerID == playerID
        )
        cards: List[MovementCard] = []
        for card in cards_db:
            isUsed = self.was_card_used_in_partial_movement(gameID, playerID, card.cardID)
            cards.append(MovementCard(type=card.type, cardID=card.cardID, isUsed=isUsed))

        return cards

    def was_card_used_in_partial_movement(self, gameID: int, playerID: int, cardID: int) -> bool:
        # IMPLEMENTAR ESTO EN EL TICKET DE MOVIMIENTOS PARCIALES
        # IMPLEMENTAR ESTO EN EL TICKET DE MOVIMIENTOS PARCIALES
        # IMPLEMENTAR ESTO EN EL TICKET DE MOVIMIENTOS PARCIALES
        return False

    def is_player_in_game(self, playerID, gameID):
        players = self.get_players(gameID)
        return playerID in [player.playerID for player in players]

    def get_public_info(self, gameID: int, playerID: int) -> GamePublicInfo:
        game = self.get(gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")

        player = self.db_session.get(PlayerDB, playerID)
        if player is None:
            raise ValueError(f"Player with ID {playerID} not found")

        return GamePublicInfo(
            gameID=game.gameID,
            board=game.board,
            prohibitedColor=game.prohibitedColor,
            posEnabledToPlay=game.posEnabledToPlay,
            players=game.players,
            figuresToUse=self.get_available_figures(gameID),
            cardsMovement=self.get_player_movement_cards(gameID, playerID),
        )

    def get_available_figures(self, gameID: int) -> list:
        # IMPLEMENTAR ESTO EN EL TICKET DE MARCAR FIGURAS DISPONIBLES
        # IMPLEMENTAR ESTO EN EL TICKET DE MARCAR FIGURAS DISPONIBLES
        # IMPLEMENTAR ESTO EN EL TICKET DE MARCAR FIGURAS DISPONIBLES
        return []

    def set_player_inactive(self, playerID: int, roomID: int) -> None:
        self.db_session.query(PlayerRoomDB).filter(
            PlayerRoomDB.playerID == playerID, PlayerRoomDB.roomID == roomID
        ).update({"isActive": False})
        self.db_session.commit()

    def is_player_active(self, playerID: int, roomID: int) -> bool:
        player = (
            self.db_session.query(PlayerRoomDB)
            .filter(PlayerRoomDB.playerID == playerID, PlayerRoomDB.roomID == roomID)
            .one_or_none()
        )
        return player is not None and player.isActive

    def get_active_players(self, gameID: int) -> List[PlayerPublicInfo]:
        players = self.get_players(gameID)
        active_players = [player for player in players if self.is_player_active(player.playerID, gameID)]
        return active_players


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
        game = self.get_public_info(gameID, playerID)
        game_json = game.model_dump()
        await ws_manager_game.send_personal_message(MessageType.STATUS, game_json, websocket)
        await ws_manager_game.keep_listening(websocket)

    async def broadcast_status_game(self, gameID: int) -> None:
        """Envia el estado actual de la sala a todos los jugadores

        Args:
            gameID (int): ID del juego
        """
        players = self.get_players(gameID)
        for player in players:
            game = self.get_public_info(gameID, player.playerID)
            game_json = game.model_dump()
            await ws_manager_game.send_personal_message_by_id(MessageType.STATUS, game_json, player.playerID, gameID)

    async def broadcast_end_game(self, gameID: int, winnerID: int) -> None:
        """Envia un mensaje de fin de juego a todos los jugadores

        Args:
            gameID (int): ID del juego
            winnerID (int): ID del jugador ganador
        """
        players = self.get_players(gameID)
        winner = Winner(playerID=winnerID, username=self.db_session.get(PlayerDB, winnerID).username)
        winner_json = winner.model_dump()
        for player in players:
            await ws_manager_game.send_personal_message_by_id(MessageType.END, winner_json, player.playerID, gameID)
