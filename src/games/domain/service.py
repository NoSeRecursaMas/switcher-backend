import random
from typing import Dict, List, Optional, Union

import numpy as np
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.games.config import COLORS, FIGURE_CARDS_FORM
from src.games.domain.models import MovementCardRequest
from src.games.domain.repository import BoardPiecePosition, GameRepository
from src.rooms.domain.repository import RoomRepository


class RepositoryValidators:
    def __init__(self, game_repository: GameRepository, room_repository: Optional[RoomRepository] = None):
        self.game_repository = game_repository
        self.room_repository = room_repository

        self.movement_validators = {
            "mov01": self.validate_mov1,
            "mov02": self.validate_mov2,
            "mov03": self.validate_mov3,
            "mov04": self.validate_mov4,
            "mov05": self.validate_mov5,
            "mov06": self.validate_mov6,
            "mov07": self.validate_mov7,
        }

    def partial_movement_exists(self, gameID: int):
        if self.game_repository.partial_movement_exists(gameID):
            return
        raise HTTPException(status_code=403, detail="El jugador no ha realizado ningún movimiento.")

    def validate_card_is_partial_movement(self, gameID: int, cardID: int):
        if not self.game_repository.was_card_used_in_partial_movement(gameID, cardID):
            return
        raise HTTPException(status_code=403, detail="La carta ya fue usada en un movimiento parcial.")

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

    def validate_card_is_not_blocked(self, cardID: int):
        if self.game_repository.is_not_blocked(cardID):
            return
        raise HTTPException(status_code=403, detail="La carta esta bloqueada.")

    async def validate_game_exists(self, gameID: int, websocket: Optional[WebSocket] = None):
        if self.game_repository.get(gameID) is not None:
            return
        if websocket is None:
            raise HTTPException(status_code=404, detail="El juego no existe.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4004, "El juego no existe.")

    def validate_target_has_three_cards(self, gameID: int, targetID: int):
        if self.game_repository.has_three_cards(gameID, targetID):
            return
        raise HTTPException(status_code=403, detail="El jugador tiene menos de tres cartas de figura.")

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

    def validate_figure_card_exists(self, gameID: int, figureCardID: int):
        card = self.game_repository.get_figure_card(figureCardID)

        if card is None or card.gameID != gameID:
            raise HTTPException(status_code=403, detail="La carta no existe en la partida.")

    def validate_figure_card_belongs_to_player(self, playerID: int, figureCardID: int):
        card = self.game_repository.get_figure_card(figureCardID)
        if card is None:
            raise HTTPException(status_code=403, detail="La carta no existe.")

        if card.playerID != playerID:
            raise HTTPException(status_code=403, detail="La carta no pertenece al jugador.")

    def validate_figure_is_empty(self, figure: List[BoardPiecePosition]):
        if len(figure) == 0:
            raise HTTPException(status_code=403, detail="La figura no puede estar vacía.")

    def validate_figure_matches_board(self, gameID: int, figure: List[BoardPiecePosition]):
        board = self.game_repository.get_board(gameID)

        color_figure = [board[piece.posX * 6 + piece.posY].color for piece in figure]
        if len(set(color_figure)) != 1:
            raise HTTPException(status_code=403, detail="La figura debe ser del mismo color.")

    def validate_figure_matches_card(self, figureID: int, figure: List[BoardPiecePosition]):
        card = self.game_repository.get_figure_card(figureID)

        if card is not None:
            figure_card_form = FIGURE_CARDS_FORM[card.type]
        else:
            raise HTTPException(status_code=403, detail="La carta no existe.")

        rotated_figures = [np.rot90(figure_card_form, k) for k in range(4)]

        min_x = min(figure, key=lambda x: x.posX).posX
        min_y = min(figure, key=lambda x: x.posY).posY
        max_x = max(figure, key=lambda x: x.posX).posX - min_x
        max_y = max(figure, key=lambda x: x.posY).posY - min_y

        figure_form = np.zeros((max_x + 1, max_y + 1), dtype=int)

        for piece in figure:
            adjusted_x = piece.posX - min_x
            adjusted_y = piece.posY - min_y
            figure_form[adjusted_x][adjusted_y] = 1

        for rotated_figure in rotated_figures:
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

    def validate_is_blocked_and_the_last_card(self, gameID: int, cardID: int):
        if not self.game_repository.is_blocked_and_last_card(gameID, cardID):
            return
        raise HTTPException(
            status_code=403, detail="No se puede jugar la carta dado que no es la ultima carta y esta bloqueada."
        )

    async def validate_player_turn(self, playerID: int, gameID: int, websocket: Optional[WebSocket] = None):
        if self.game_repository.is_player_turn(playerID, gameID):
            return
        if websocket is None:
            raise HTTPException(status_code=403, detail="No es el turno del jugador.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4005, "No es el turno del jugador.")

    def validate_movement_card(self, request: MovementCardRequest) -> bool:
        if request.origin.posX < 0 or request.origin.posX > 5:
            raise ValueError("Posicion de origen fuera del tablero")
        if request.origin.posY < 0 or request.origin.posY > 5:
            raise ValueError("Posicion de origen fuera del tablero")
        if request.destination.posX < 0 or request.destination.posX > 5:
            raise ValueError("Posicion de destino fuera del tablero")
        if request.destination.posY < 0 or request.destination.posY > 5:
            raise ValueError("Posicion de destino fuera del tablero")

        movement_card = self.game_repository.get_movement_card(request.cardID)
        if movement_card is None:
            raise ValueError("No existe carta de movimiento")

        if movement_card.type not in self.movement_validators:
            raise ValueError("No existe carta de movimiento")

        if not self.movement_validators[movement_card.type](request):
            raise HTTPException(status_code=403, detail="Movimiento inválido.")

        return True

    def card_exists(self, cardID: int):
        if self.game_repository.card_exists(cardID):
            return
        raise HTTPException(status_code=403, detail="La carta de movimiento no existe.")

    def has_movement_card(self, playerID: int, cardID: int):
        if self.game_repository.has_movement_card(playerID, cardID):
            return
        raise HTTPException(status_code=403, detail="El jugador no tiene la carta de movimiento.")

    def mov_calc(self, request: MovementCardRequest):
        deltaX = abs(request.origin.posX - request.destination.posX)
        deltaY = abs(request.origin.posY - request.destination.posY)
        return deltaX, deltaY

    def validate_mov1(self, request: MovementCardRequest) -> bool:
        deltaX, deltaY = self.mov_calc(request)
        return deltaX == 2 and deltaY == 2

    def validate_mov2(self, request: MovementCardRequest) -> bool:
        deltaX, deltaY = self.mov_calc(request)
        return (deltaX == 0 and deltaY == 2) or (deltaX == 2 and deltaY == 0)

    def validate_mov3(self, request: MovementCardRequest) -> bool:
        deltaX, deltaY = self.mov_calc(request)
        return (deltaX == 0 and deltaY == 1) or (deltaX == 1 and deltaY == 0)

    def validate_mov4(self, request: MovementCardRequest) -> bool:
        deltaX, deltaY = self.mov_calc(request)
        return deltaX == 1 and deltaY == 1

    def validate_mov5(self, request: MovementCardRequest) -> bool:
        up_posX_correct = (request.origin.posX - 2) == request.destination.posX
        up_posY_correct = (request.origin.posY + 1) == request.destination.posY
        up_correct = up_posX_correct and up_posY_correct

        down_posX_correct = (request.origin.posX + 2) == request.destination.posX
        down_posY_correct = (request.origin.posY - 1) == request.destination.posY
        down_correct = down_posX_correct and down_posY_correct

        posX_correct_right = (request.origin.posX + 1) == request.destination.posX
        posY_correct_rigth = (request.origin.posY + 2) == request.destination.posY
        correct_right = posX_correct_right and posY_correct_rigth

        posX_correct_left = (request.origin.posX - 1) == request.destination.posX
        posY_correct_left = (request.origin.posY - 2) == request.destination.posY
        correct_left = posX_correct_left and posY_correct_left

        return up_correct or down_correct or correct_right or correct_left

    def validate_mov6(self, request: MovementCardRequest) -> bool:
        up_posX_correct = (request.origin.posX - 2) == request.destination.posX
        up_posY_correct = (request.origin.posY - 1) == request.destination.posY
        up_correct = up_posX_correct and up_posY_correct

        down_posX_correct = (request.origin.posX + 2) == request.destination.posX
        down_posY_correct = (request.origin.posY + 1) == request.destination.posY
        down_correct = down_posX_correct and down_posY_correct

        posX_correct_right = (request.origin.posX - 1) == request.destination.posX
        posY_correct_rigth = (request.origin.posY + 2) == request.destination.posY
        correct_right = posX_correct_right and posY_correct_rigth

        posX_correct_left = (request.origin.posX + 1) == request.destination.posX
        posY_correct_left = (request.origin.posY - 2) == request.destination.posY
        correct_left = posX_correct_left and posY_correct_left

        return up_correct or down_correct or correct_right or correct_left

    def validate_mov7(self, request: MovementCardRequest) -> bool:
        deltaX, deltaY = self.mov_calc(request)
        posX_non_affected = deltaX == 0
        posY_non_affected = deltaY == 0
        right_side = posX_non_affected and request.destination.posY == 5
        left_side = posX_non_affected and request.destination.posY == 0
        top_side = request.destination.posX == 5 and posY_non_affected
        bottom_side = request.destination.posX == 0 and posY_non_affected

        return right_side or left_side or top_side or bottom_side

    def validate_prohibited_color(self, gameID: int, figure: List[BoardPiecePosition]):
        prohibited_color = self.game_repository.get_prohibited_color(gameID)
        board = self.game_repository.get_board(gameID)

        if board[figure[0].posX * 6 + figure[0].posY].color == prohibited_color:
            raise HTTPException(status_code=403, detail="La figura no puede ser del color prohibido.")


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

    def set_game_turn_order(self, gameID: int) -> int:
        players = self.game_repository.get_players(gameID)
        player_count = len(players)
        positions = list(range(1, player_count + 1))

        random.shuffle(positions)

        for player, position in zip(players, positions):
            self.room_repository.set_position(player.playerID, position, gameID)

        return self.room_repository.get_first_turn(gameID)
