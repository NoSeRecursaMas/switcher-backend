import json
import random
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import numpy as np
from fastapi.websockets import WebSocket
from scipy.signal import convolve2d
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from src.games.config import (
    BLUE_CARDS,
    BLUE_CARDS_AMOUNT,
    COLORS,
    FIGURE_CARDS_FORM,
    FIGURE_CARDS_NAMES,
    MOVEMENT_CARDS,
    MOVEMENT_CARDS_AMOUNT,
    MOVEMENT_CARDS_NAMES,
    WHITE_CARDS,
    WHITE_CARDS_AMOUNT,
)
from src.games.domain.models import (
    BoardPiece,
    BoardPiecePosition,
    FigureCard,
    Game,
    GameID,
    GamePublicInfo,
    MovementCard,
    PlayerPublicInfo,
    Position,
    Winner,
)
from src.games.domain.models import (
    MovementCard as MovementCardDomain,
)
from src.games.domain.repository import GameRepository, GameRepositoryWS
from src.games.infrastructure.models import FigureCard as FigureCardDB
from src.games.infrastructure.models import Game as GameDB
from src.games.infrastructure.models import MovementCard as MovementCardDB
from src.games.infrastructure.websocket import MessageType, ws_manager_game
from src.players.infrastructure.models import Player as PlayerDB
from src.rooms.infrastructure.models import PlayerRoom as PlayerRoomDB
from src.rooms.infrastructure.models import Room as RoomDB
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

    def skip(self, gameID: int) -> int:
        game = self.db_session.get(GameDB, gameID)
        game_players = self.get_players(gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")
        current_position = game.posEnabledToPlay

        if current_position == len(game_players):
            game.posEnabledToPlay = 1
        else:
            game.posEnabledToPlay = current_position + 1

        self.db_session.commit()

        # Caso en el que el jugador que ahora tiene el turno no está activo
        for player in game_players:
            if player.position == game.posEnabledToPlay and not player.isActive:
                return self.skip(gameID)

        self.db_session.commit()

        return game.posEnabledToPlay

    def rebuild_movement_deck(self, gameID: int) -> None:
        movement_cards = (
            self.db_session.query(MovementCardDB)
            .filter(MovementCardDB.gameID == gameID, MovementCardDB.playerID.is_(None))
            .all()
        )

        for card in movement_cards:
            card.isDiscarded = False

        self.db_session.commit()

    def replacement_movement_card(self, gameID: int, playerID: int) -> None:
        playable_cards = self.db_session.query(MovementCardDB).filter(
            MovementCardDB.gameID == gameID, MovementCardDB.playerID == playerID
        )

        if playable_cards.count() < 3:
            available_cards = (
                self.db_session.query(MovementCardDB)
                .filter(
                    MovementCardDB.gameID == gameID,
                    MovementCardDB.isDiscarded.is_(False),
                    MovementCardDB.playerID.is_(None),
                )
                .order_by(func.random())
                .limit(3 - playable_cards.count())
            )

            if available_cards.count() < 3 - playable_cards.count():
                self.rebuild_movement_deck(gameID)
                available_cards = (
                    self.db_session.query(MovementCardDB)
                    .filter(
                        MovementCardDB.gameID == gameID,
                        MovementCardDB.isDiscarded.is_(False),
                        MovementCardDB.playerID.is_(None),
                    )
                    .order_by(func.random())
                    .limit(3 - playable_cards.count())
                )

            for card in available_cards:
                card.playerID = playerID

        self.db_session.commit()

    def replacement_figure_card(self, gameID: int, playerID: int) -> None:
        figure_cards = self.db_session.query(FigureCardDB).filter(
            FigureCardDB.gameID == gameID,
            FigureCardDB.playerID == playerID,
            FigureCardDB.isPlayable,
        )

        blocked = any([card.isBlocked for card in figure_cards])
        wasBlocked = any([card.wasBlocked for card in figure_cards])

        if blocked or wasBlocked:
            return

        available_cards = (
            self.db_session.query(FigureCardDB)
            .filter(
                FigureCardDB.gameID == gameID, FigureCardDB.playerID == playerID, FigureCardDB.isPlayable.is_(False)
            )
            .limit(3 - figure_cards.count())
        )

        for card in available_cards:
            card.isPlayable = True

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

    def board_piece_to_dict(self, piece):
        return {"posX": piece.posX, "posY": piece.posY, "color": piece.color}

    def play_movement(
        self, gameID: int, card_id: int, originX: int, originY: int, destinationX: int, destinationY: int
    ) -> None:
        game = self.db_session.get(GameDB, gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")
        board = self.get_board(gameID)
        origin_piece = next(piece for piece in board if piece.posX == originX and piece.posY == originY)
        destination_piece = next(piece for piece in board if piece.posX == destinationX and piece.posY == destinationY)
        aux = origin_piece.color
        origin_piece.color = destination_piece.color
        destination_piece.color = aux

        last_movements = json.loads(game.lastMovements) if game.lastMovements else []

        last_movements.append(
            {
                "CardID": card_id,
                "origin": self.board_piece_to_dict(origin_piece),
                "destination": self.board_piece_to_dict(destination_piece),
                "Order": len(last_movements) + 1,
            }
        )

        game.lastMovements = json.dumps(last_movements)

        game.board = json.dumps([self.board_piece_to_dict(piece) for piece in board])
        self.db_session.commit()

    def has_three_cards(self, gameID: int, playerID: int) -> bool:
        cards = (
            self.db_session.query(FigureCardDB)
            .filter(FigureCardDB.gameID == gameID, FigureCardDB.playerID == playerID, FigureCardDB.isPlayable.is_(True))
            .all()
        )
        return len(cards) == 3

    def partial_movement_exists(self, gameID: int) -> bool:
        game = self.db_session.get(GameDB, gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")
        return len(json.loads(game.lastMovements)) > 0

    def delete_partial_movement(self, gameID: int) -> None:
        game = self.db_session.get(GameDB, gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")

        last_movements = json.loads(game.lastMovements) if game.lastMovements else []
        if len(last_movements) == 0:
            return

        last_movement = last_movements[-1]
        last_movement_origin = last_movement["origin"]
        last_movement_destination = last_movement["destination"]
        board = self.get_board(gameID)
        origin_piece = next(
            piece
            for piece in board
            if piece.posX == last_movement_origin["posX"] and piece.posY == last_movement_origin["posY"]
        )
        destination_piece = next(
            piece
            for piece in board
            if piece.posX == last_movement_destination["posX"] and piece.posY == last_movement_destination["posY"]
        )
        aux = origin_piece.color
        origin_piece.color = destination_piece.color
        destination_piece.color = aux
        game.lastMovements = json.dumps(last_movements[:-1])
        game.board = json.dumps([self.board_piece_to_dict(piece) for piece in board])
        self.db_session.commit()

    def has_movement_card(self, playerID: int, cardID: int) -> bool:
        card = self.db_session.get(MovementCardDB, cardID)
        if card is None:
            raise ValueError(f"Card with ID {cardID} not found")
        return card.playerID == playerID

    def card_exists(self, cardID: int) -> bool:
        card = self.db_session.get(MovementCardDB, cardID)
        return card is not None

    def is_player_turn(self, playerID: int, gameID: int) -> bool:
        game = self.db_session.get(GameDB, gameID)
        players = self.get_players(gameID)
        player = next(player for player in players if player.playerID == playerID)
        return player.position == game.posEnabledToPlay

    def is_piece_partial(self, gameID: int, posX: int, posY: int) -> bool:
        game = self.db_session.get(GameDB, gameID)
        last_movements = json.loads(game.lastMovements) if game.lastMovements else []
        for movement in last_movements:
            if movement["origin"]["posX"] == posX and movement["origin"]["posY"] == posY:
                return True
            if movement["destination"]["posX"] == posX and movement["destination"]["posY"] == posY:
                return True
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
        amount_non_playable = figure_cards.filter(FigureCardDB.isPlayable.is_(False)).count()

        playable_cards: List[FigureCard] = []
        for card in figure_cards:
            if card.isPlayable:
                playable_cards.append(
                    FigureCard(
                        type=card.type,
                        cardID=card.cardID,
                        isBlocked=card.isBlocked,
                        gameID=card.gameID,
                        playerID=card.playerID,
                    )
                )

        return amount_non_playable, playable_cards

    def get_player_movement_cards(self, gameID: int, playerID: int) -> List[MovementCard]:
        cards_db = self.db_session.query(MovementCardDB).filter(
            MovementCardDB.gameID == gameID, MovementCardDB.playerID == playerID
        )
        cards: List[MovementCard] = []
        for card in cards_db:
            isUsed = self.was_card_used_in_partial_movement(gameID, card.cardID)
            cards.append(MovementCard(type=card.type, cardID=card.cardID, isUsed=isUsed))

        return cards

    def clean_partial_movements(self, gameID: int) -> None:
        game = self.db_session.get(GameDB, gameID)
        last_movements = json.loads(game.lastMovements) if game.lastMovements else []
        board = self.get_board(gameID)
        last_movements.sort(key=lambda x: x["Order"], reverse=True)
        for movement in last_movements:
            origin = movement["origin"]
            destination = movement["destination"]
            origin_piece = next(
                piece for piece in board if piece.posX == origin["posX"] and piece.posY == origin["posY"]
            )
            destination_piece = next(
                piece for piece in board if piece.posX == destination["posX"] and piece.posY == destination["posY"]
            )
            aux = origin_piece.color
            origin_piece.color = destination_piece.color
            destination_piece.color = aux
        game.board = json.dumps([self.board_piece_to_dict(piece) for piece in board])
        game.lastMovements = json.dumps([])
        self.db_session.commit()

    def set_partial_movements_to_empty(self, gameID: int) -> None:
        game = self.db_session.get(GameDB, gameID)
        game.lastMovements = json.dumps([])
        self.db_session.commit()

    def was_card_used_in_partial_movement(self, gameID: int, cardID: int) -> bool:
        game = self.db_session.get(GameDB, gameID)
        last_movements = json.loads(game.lastMovements) if game.lastMovements else []
        for movement in last_movements:
            if movement["CardID"] == cardID:
                return True
        return False

    def is_player_in_game(self, playerID, gameID):
        players = self.get_players(gameID)
        return playerID in [player.playerID for player in players]

    def get_current_turn(self, gameID: int) -> int:
        game = self.get(gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")
        return game.posEnabledToPlay

    def get_position_player(self, gameID, playerID):
        game = self.db_session.get(GameDB, gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")
        player_position = (
            self.db_session.query(PlayerRoomDB)
            .filter(PlayerRoomDB.playerID == playerID, PlayerRoomDB.roomID == game.roomID)
            .one_or_none()
            .position
        )
        return player_position

    def get_public_info(self, gameID: int, playerID: int) -> GamePublicInfo:
        game = self.get(gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")

        player = self.db_session.get(PlayerDB, playerID)
        if player is None:
            raise ValueError(f"Player with ID {playerID} not found")

        timestamp = self.db_session.get(GameDB, gameID).timestamp_next_turn
        if timestamp is None:
            timestamp = datetime.now()

        return GamePublicInfo(
            gameID=game.gameID,
            board=game.board,
            figuresToUse=self.get_available_figures(game.prohibitedColor, self.get_board(gameID)),
            prohibitedColor=game.prohibitedColor,
            posEnabledToPlay=game.posEnabledToPlay,
            players=game.players,
            timer=timedelta.total_seconds(timestamp - datetime.now()),
        )

    def add_movement_cards_to_public_info(self, gameID: int, playerID: int, game: GamePublicInfo):
        game_json = game.model_dump()

        for player in game_json["players"]:
            player["sizeDeckFigure"], _ = self.get_player_figure_cards(gameID, player["playerID"])
            if player["playerID"] == playerID:
                player["cardsMovement"] = []
                for card in self.get_player_movement_cards(gameID, playerID):
                    player["cardsMovement"].append(card.model_dump())
            else:
                cards_db = self.db_session.query(MovementCardDB).filter(
                    MovementCardDB.gameID == gameID, MovementCardDB.playerID == player["playerID"]
                )
                cards = []
                for card in cards_db:
                    isUsed = self.was_card_used_in_partial_movement(gameID, card.cardID)
                    if isUsed:
                        cards.append(MovementCard(type=card.type, cardID=card.cardID, isUsed=isUsed).model_dump())
                    else:
                        cards.append(None)

                player["cardsMovement"] = cards

        return game_json

    def get_available_figures(
        self, prohibitedColor: Optional[str], board: List[BoardPiece]
    ) -> List[List[BoardPiecePosition]]:
        board_matrix = np.empty((6, 6), dtype=object)

        for piece in board:
            board_matrix[piece.posY][piece.posX] = piece.color

        prohibitedColor = prohibitedColor or ""

        color_layers = self.create_color_layers(board_matrix, prohibitedColor)

        all_figures = []
        rotated_figures = {
            figure_type: [np.rot90(shape, k) for k in range(4)] for figure_type, shape in FIGURE_CARDS_FORM.items()
        }

        seen_figures = set()

        for color, layer in color_layers.items():
            for figure_type, rotations in rotated_figures.items():
                for rotated_figure in rotations:
                    figures_found = self.match_figure_in_layer(rotated_figure, layer)

                    for figure in figures_found:
                        figure_tuple = tuple((pos.posX, pos.posY) for pos in figure)

                        if figure_tuple not in seen_figures:
                            seen_figures.add(figure_tuple)
                            all_figures.append(figure)

        return all_figures

    def create_color_layers(self, board_matrix: np.ndarray, prohibitedColor: str) -> dict:
        return {color: (board_matrix == color).astype(int) for color in COLORS if color != prohibitedColor}

    def match_figure_in_layer(self, shape: np.ndarray, layer: np.ndarray) -> List[List[BoardPiecePosition]]:
        matched_figures = []
        shape_height, shape_width = shape.shape

        result = convolve2d(layer, shape[::-1, ::-1], mode="valid")

        for y, x in zip(*np.where(result == shape.sum())):
            matched_positions = [
                BoardPiecePosition(posX=x + shape_x, posY=y + shape_y)
                for shape_y in range(shape_height)
                for shape_x in range(shape_width)
                if shape[shape_y, shape_x] == 1
            ]

            if self.check_border_validity(matched_positions, layer):
                matched_figures.append(matched_positions)

        return matched_figures

    def check_border_validity(self, positions: List[BoardPiecePosition], layer: np.ndarray) -> bool:
        position_set = {(pos.posX, pos.posY) for pos in positions}
        for pos in positions:
            x, y = pos.posX, pos.posY
            adjacent_positions = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]

            for nx, ny in adjacent_positions:
                if 0 <= nx < 6 and 0 <= ny < 6 and (nx, ny) not in position_set:
                    if layer[ny, nx] == layer[y, x]:
                        return False
        return True

    def set_player_inactive(self, playerID: int, gameID: int) -> None:
        game = self.db_session.get(GameDB, gameID)
        self.db_session.query(PlayerRoomDB).filter(
            PlayerRoomDB.playerID == playerID, PlayerRoomDB.roomID == game.roomID
        ).update({"isActive": False})
        figure_cards = self.db_session.query(FigureCardDB).filter(
            FigureCardDB.playerID == playerID, FigureCardDB.gameID == gameID
        )
        for card in figure_cards:
            self.db_session.delete(card)
        movement_cards = self.db_session.query(MovementCardDB).filter(
            MovementCardDB.playerID == playerID, MovementCardDB.gameID == gameID
        )
        for card in movement_cards:
            card.isDiscarded = True
            card.playerID = None

        if game.posEnabledToPlay == self.get_position_player(gameID, playerID):
            if game.posEnabledToPlay == len(self.get_players(gameID)):
                game.posEnabledToPlay = 1
            else:
                game.posEnabledToPlay += 1

        self.db_session.commit()

    def is_player_active(self, playerID: int, gameID: int) -> bool:
        roomID = self.db_session.get(GameDB, gameID).roomID
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

    def delete_and_clean(self, gameID: int) -> None:
        game = self.db_session.get(GameDB, gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")
        self.db_session.query(FigureCardDB).filter(FigureCardDB.gameID == gameID).delete()
        self.db_session.query(MovementCardDB).filter(MovementCardDB.gameID == gameID).delete()
        self.db_session.query(PlayerRoomDB).filter(PlayerRoomDB.roomID == game.roomID).delete()
        room = game.room
        self.db_session.delete(game)
        self.db_session.delete(room)
        self.db_session.commit()

    def play_figure(self, gameID: int, figureID: int, figure: List[BoardPiecePosition]) -> None:
        figure_card = self.db_session.query(FigureCardDB).filter_by(cardID=figureID).first()

        if figure_card:
            self.db_session.delete(figure_card)
            color = self.get_color_from_position(gameID, figure[0].posX, figure[0].posY)
            self.change_color_prohibited(gameID, color)
            self.db_session.commit()

    def get_color_from_position(self, gameID: int, posX: int, posY: int) -> str:
        game = self.db_session.get(GameDB, gameID)
        board = json.loads(game.board)
        piece = next(piece for piece in board if piece["posX"] == posX and piece["posY"] == posY)
        return piece["color"]

    def change_color_prohibited(self, gameID: int, color: str) -> None:
        game = self.db_session.get(GameDB, gameID)
        game.prohibitedColor = color
        self.db_session.commit()

    def get_figure_card(self, figureCardID: int) -> Optional[FigureCard]:
        card = self.db_session.get(FigureCardDB, figureCardID)
        if card is None:
            return None
        return FigureCard(
            type=card.type, cardID=card.cardID, isBlocked=card.isBlocked, gameID=card.gameID, playerID=card.playerID
        )

    def desvinculate_partial_movement_cards(self, gameID):
        game = self.db_session.get(GameDB, gameID)
        last_movements = json.loads(game.lastMovements) if game.lastMovements else []
        for movement in last_movements:
            card = self.db_session.get(MovementCardDB, movement["CardID"])
            card.playerID = None
            card.isDiscarded = True
        self.db_session.commit()

    def get_movement_card(self, cardID: int) -> MovementCardDomain:
        card = self.db_session.get(MovementCardDB, cardID)
        if card is None:
            raise ValueError(f"Card with ID {cardID} not found")
        return MovementCardDomain(type=card.type, cardID=card.cardID, isUsed=card.isDiscarded)

    def get_prohibited_color(self, gameID: int) -> str:
        game = self.db_session.get(GameDB, gameID)
        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")
        return game.prohibitedColor

    def figure_card_count(self, gameID: int, playerID: int) -> int:
        return (
            self.db_session.query(FigureCardDB)
            .filter(FigureCardDB.gameID == gameID, FigureCardDB.playerID == playerID)
            .count()
        )

    def is_blocked_and_last_card(self, gameID: int, cardID: int):
        is_last_card = False
        game = self.db_session.get(GameDB, gameID)
        card = self.db_session.get(FigureCardDB, cardID)
        cards_with_playerID = (
            self.db_session.query(FigureCardDB)
            .filter(
                FigureCardDB.gameID == gameID, FigureCardDB.playerID == card.playerID, FigureCardDB.isPlayable.is_(True)
            )
            .all()
        )
        if len(cards_with_playerID) == 1:
            is_last_card = True
        return card.isBlocked and is_last_card

    def unblock_managment(self, gameID: int, blockedcardID: int) -> None:
        card = self.db_session.get(FigureCardDB, blockedcardID)
        if card is None:
            raise ValueError(f"Card with ID {blockedcardID} not found")

        blocked_player_cards = (
            self.db_session.query(FigureCardDB)
            .filter(
                FigureCardDB.gameID == gameID, FigureCardDB.playerID == card.playerID, FigureCardDB.isBlocked.is_(True)
            )
            .all()
        )

        if len(blocked_player_cards) == 1:
            card.isBlocked = False
            card.wasBlocked = True

        self.db_session.commit()

    def block_managment(self, gameID: int, figureID: int, figure: List[BoardPiecePosition]) -> None:
        card = self.db_session.get(FigureCardDB, figureID)
        cards_from_player = (
            self.db_session.query(FigureCardDB)
            .filter(
                FigureCardDB.gameID == gameID, FigureCardDB.playerID == card.playerID, FigureCardDB.isPlayable.is_(True)
            )
            .all()
        )
        for cards in cards_from_player:
            blocked_player_cards = (
                self.db_session.query(FigureCardDB)
                .filter(
                    FigureCardDB.gameID == gameID,
                    FigureCardDB.playerID == card.playerID,
                    FigureCardDB.isBlocked.is_(True),
                    FigureCardDB.isPlayable.is_(True),
                )
                .all()
            )
            if len(blocked_player_cards) == 0:
                card.isBlocked = True
            self.db_session.commit()

        color = self.get_color_from_position(gameID, figure[0].posX, figure[0].posY)
        self.change_color_prohibited(gameID, color)
        self.db_session.commit()

    def is_not_blocked(self, cardID: int) -> bool:
        card = self.db_session.get(FigureCardDB, cardID)
        return not card.isBlocked

    def get_blocked_card(self, gameID: int, playerID: int) -> Optional[int]:
        card = (
            self.db_session.query(FigureCardDB)
            .filter(FigureCardDB.gameID == gameID, FigureCardDB.playerID == playerID, FigureCardDB.isBlocked.is_(True))
            .first()
        )

        if card is None:
            return None

        return card.cardID

    def card_was_blocked(self, cardID: int) -> bool:
        card = self.db_session.get(FigureCardDB, cardID)
        return card.wasBlocked

    def set_was_blocked_false(self, cardID: int) -> None:
        card = self.db_session.get(FigureCardDB, cardID)
        card.wasBlocked = False
        self.db_session.commit()

    def get_current_timestamp_next_turn(self, gameID: int) -> datetime:
        game = self.db_session.get(GameDB, gameID)
        return game.timestamp_next_turn

    def set_timestamp_next_turn(self, gameID: int, timestamp: datetime) -> None:
        game = self.db_session.get(GameDB, gameID)
        game.timestamp_next_turn = timestamp
        self.db_session.commit()


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
        game_json = self.add_movement_cards_to_public_info(gameID, playerID, game)
        await ws_manager_game.send_personal_message(MessageType.STATUS, game_json, websocket)
        await ws_manager_game.keep_listening(websocket, gameID)

    async def broadcast_status_game(self, gameID: int) -> None:
        """Envia el estado actual de la sala a todos los jugadores

        Args:
            gameID (int): ID del juego
        """
        players = self.get_players(gameID)
        for player in players:
            game = self.get_public_info(gameID, player.playerID)
            game_json = self.add_movement_cards_to_public_info(gameID, player.playerID, game)
            await ws_manager_game.send_personal_message_by_id(MessageType.STATUS, game_json, player.playerID, gameID)

    async def broadcast_end_game(self, gameID: int, winnerID: int) -> None:
        """Envia un mensaje de fin de juego a todos los jugadores

        Args:
            gameID (int): ID del juego
            winnerID (int): ID del jugador ganador
        """
        players = self.get_players(gameID)
        winner = Winner(winnerID=winnerID, username=self.db_session.get(PlayerDB, winnerID).username)
        winner_json = winner.model_dump()
        for player in players:
            await ws_manager_game.send_personal_message_by_id(MessageType.END, winner_json, player.playerID, gameID)

    async def send_log_play_movement_card(self, gameID: int, playerID: int, cardID: int) -> None:
        card = self.get_movement_card(cardID)
        card_name = MOVEMENT_CARDS_NAMES[card.type]
        player = self.db_session.get(PlayerDB, playerID)
        player_name = player.username

        message = f"{player_name} ha jugado la carta de movimiento '{card_name}'"

        data = {"username": "⚙️ Sistema ⚙️", "text": message}

        await ws_manager_game.broadcast(MessageType.MSG, data, gameID)

    async def send_log_cancel_movement_card(self, gameID: int, playerID: int) -> None:
        game = self.db_session.get(GameDB, gameID)

        if game is None:
            raise ValueError(f"Game with ID {gameID} not found")

        last_movements = json.loads(game.lastMovements) if game.lastMovements else []

        if len(last_movements) == 0:
            return

        card = self.get_movement_card(last_movements[-1]["CardID"])
        card_name = MOVEMENT_CARDS_NAMES[card.type]
        player = self.db_session.get(PlayerDB, playerID)
        player_name = player.username

        message = f"{player_name} ha cancelado el movimiento realizado por la carta '{card_name}'"

        data = {"username": "⚙️ Sistema ⚙️", "text": message}

        await ws_manager_game.broadcast(MessageType.MSG, data, gameID)

    async def remove_player(self, playerID: int, gameID: int) -> None:
        """Remueve al jugador de la lista de conexiones activas

        Args:
            playerID (int): ID del jugador
            gameID (int): ID del juego
        """
        await ws_manager_game.disconnect_by_id(playerID, gameID)

    async def send_log_player_leave_game(self, gameID: int, playerID: int) -> None:
        player = self.db_session.get(PlayerDB, playerID)
        player_name = player.username

        message = f"{player_name} ha abandonado la partida"

        data = {"username": "⚙️ Sistema ⚙️", "text": message}

        await ws_manager_game.broadcast(MessageType.MSG, data, gameID)

    async def send_log_play_figure(self, gameID: int, playerID: int, figureID: int) -> None:
        card = self.get_figure_card(figureID)
        if card is None:
            raise ValueError(f"Card with ID {figureID} not found")
        card_name = FIGURE_CARDS_NAMES[card.type]
        player = self.db_session.get(PlayerDB, playerID)
        player_name = player.username

        message = f"{player_name} ha jugado la carta de figura '{card_name}'"

        data = {"username": "⚙️ Sistema ⚙️", "text": message}

        await ws_manager_game.broadcast(MessageType.MSG, data, gameID)

    async def send_log_block_figure(self, gameID: int, playerID: int, targetID: int, figureID: int) -> None:
        card = self.get_figure_card(figureID)
        if card is None:
            raise ValueError(f"Card with ID {figureID} not found")
        card_name = FIGURE_CARDS_NAMES[card.type]
        player = self.db_session.get(PlayerDB, playerID)
        player_name = player.username

        target_player = self.db_session.get(PlayerDB, targetID)
        target_player_name = target_player.username

        message = f"{player_name} ha bloqueado la carta de figura '{card_name}' del jugador {target_player_name}"

        data = {"username": "⚙️ Sistema ⚙️", "text": message}

        await ws_manager_game.broadcast(MessageType.MSG, data, gameID)

    async def send_log_turn_skip(self, gameID: int, playerID: int, auto: bool) -> None:
        player = self.db_session.get(PlayerDB, playerID)
        player_name = player.username

        message = f"{player_name} ha pasado su turno"

        if auto:
            message = f"El turno de {player_name} ha terminado por finalizar su tiempo de juego"

        data = {"username": "⚙️ Sistema ⚙️", "text": message}

        await ws_manager_game.broadcast(MessageType.MSG, data, gameID)
