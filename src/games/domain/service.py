import random
from typing import Dict, List, Optional, Union

import numpy as np
from fastapi import HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.games.config import COLORS, FIGURE_CARDS_FORM
from src.games.domain.repository import BoardPiecePosition, GameRepository
from src.rooms.domain.repository import RoomRepository


class RepositoryValidators:
    def __init__(self, game_repository: GameRepository, room_repository: Optional[RoomRepository] = None):
        self.game_repository = game_repository
        self.room_repository = room_repository

    def validate_min_players_to_start(self, roomID: int):
        if self.room_repository is None:
            raise ValueError("RoomRepository is required to start a game")
        room = self.room_repository.get_public_info(roomID)
        if room is None:
            raise HTTPException(status_code=404, detail="La sala no existe.")
        if len(room.players) < room.minPlayers:
            raise HTTPException(status_code=403, detail="No hay suficientes jugadores para iniciar la partida.")

    def validate_is_player_turn(self, playerID: int, gameID: int):
        postion_player = self.game_repository.get_position_player(gameID, playerID)
        if self.game_repository.get_current_turn(gameID) == postion_player:
            return
        raise HTTPException(status_code=403, detail="No es el turno del jugador.")

    async def validate_game_exists(self, gameID: int, websocket: Optional[WebSocket] = None):
        if self.game_repository.get(gameID) is not None:
            return
        if websocket is None:
            raise HTTPException(status_code=404, detail="El juego no existe.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4004, "El juego no existe.")

    async def is_player_in_game(self, playerID: int, gameID: int, websocket: Optional[WebSocket] = None):
        player_in_game = self.game_repository.is_player_in_game(playerID, gameID)
        player_active = self.game_repository.is_player_active(playerID, gameID)

        if player_in_game and player_active:
            return
        if websocket is None:
            raise HTTPException(status_code=403, detail="El jugador no se encuentra en el juego.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4003, "El jugador no se encuentra en el juego.")

    def validate_figure_card_exists(self, gameID: int, playerID: int, figureCardID: int):
        card = self.game_repository.get_figure_card(figureCardID)
        if card is not None and card.gameID == gameID and card.playerID == playerID:
            return HTTPException(status_code=403, detail="La carta no existe.")

    def validate_figure_color(self, gameID: int, figure: List[BoardPiecePosition]):
        board = self.game_repository.get_board(gameID)

        first_position = figure[0].posX * 6 + figure[0].posY

        color = board[first_position].color
        print(color)
        for piece in figure:
            position = piece.posX * 6 + piece.posY
            if board[position].color != color:
                raise HTTPException(status_code=403, detail="La figura debe tener fichas del mismo color.")

    def validate_figure_is_empty(self, figure: List[BoardPiecePosition]):
        if len(figure) == 0:
            raise HTTPException(status_code=403, detail="La figura no puede estar vacía.")

    def validate_figure_matches_board(self, gameID: int, figure: List[BoardPiecePosition]):
        board = self.game_repository.get_board(gameID)

        color_figure = [board[piece.posX * 6 + piece.posY].color for piece in figure]
        if len(set(color_figure)) != 1:
            raise HTTPException(status_code=403, detail="La figura no está en el tablero.")

    def validate_figure_matches_card(self, figureID: int, figure: List[BoardPiecePosition]):
        card = self.game_repository.get_figure_card(figureID)

        figure_card_form = FIGURE_CARDS_FORM[card.type]
        rotated_figures = [np.rot90(figure_card_form, k) for k in range(4)]

        min_x = min(figure, key=lambda x: x.posX).posX
        min_y = min(figure, key=lambda x: x.posY).posY
        max_x = max(figure, key=lambda x: x.posX).posX - min_x
        max_y = max(figure, key=lambda x: x.posY).posY - min_y

        print(max_x, max_y)

        figure_form = np.zeros((max_y + 1, max_x + 1), dtype=bool)

        for piece in figure:
            adjusted_x = piece.posX - min_x
            adjusted_y = piece.posY - min_y
            figure_form[adjusted_y][adjusted_x] = 1

        for rotated_figure in rotated_figures:
            print(rotated_figure)
            print(figure_form)
            if figure_form.shape == rotated_figure.shape and (rotated_figure == figure_form).all():
                return

        raise HTTPException(status_code=403, detail="La figura no coincide con la carta.")

    def validate_figure_border_validity(self, gameID: int, figure: List[BoardPiecePosition]):
        board = self.game_repository.get_board(gameID)

        board_matrix = np.empty((6, 6), dtype=object)

        for piece in board:
            board_matrix[piece.posY][piece.posX] = piece.color

        if not self.game_repository.check_border_validity(figure, board_matrix):
            raise HTTPException(status_code=403, detail="La figura tiene una ficha adyacente del mismo color.")


class GameServiceDomain:
    def __init__(self, game_repository: GameRepository, room_repository: RoomRepository):
        self.game_repository = game_repository
        self.room_repository = room_repository

    @staticmethod
    def create_board() -> List[Dict[str, Union[int, str]]]:
        color_pool = 9 * COLORS
        random.shuffle(color_pool)

        board = []
        for i in range(6):
            for j in range(6):
                token: Dict[str, Union[int, str]] = {}
                token["posX"] = i
                token["posY"] = j
                token["color"] = color_pool.pop()
                board.append(token)

        return board

    def set_game_turn_order(self, gameID: int) -> None:
        players = self.game_repository.get_players(gameID)
        player_count = len(players)

        positions = list(range(1, player_count + 1))

        random.shuffle(positions)

        for player, position in zip(players, positions):
            self.room_repository.set_position(player.playerID, position)
