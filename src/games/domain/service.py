import random
from typing import Dict, List, Optional, Union

from fastapi import HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.games.config import COLORS
from src.games.domain.repository import GameRepository
from src.rooms.domain.repository import RoomRepository
from src.games.domain.models import MovementCardRequest


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

    def validate_min_players_to_start(self, roomID: int):
        if self.room_repository is None:
            raise ValueError("RoomRepository is required to start a game")
        room = self.room_repository.get_public_info(roomID)
        if room is None:
            raise HTTPException(status_code=404, detail="La sala no existe.")
        if len(room.players) < room.minPlayers:
            raise HTTPException(status_code=403, detail="No hay suficientes jugadores para iniciar la partida.")

    def validate_is_player_turn(self, postion_player: int, gameID: int):
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

    async def validate_player_exists(self, playerID: int, websocket: Optional[WebSocket] = None):
        if self.room_repository is None:
            raise ValueError("RoomRepository is required to validate player exists")
        if self.room_repository.get_player(playerID) is not None:
            return
        if websocket is None:
            raise HTTPException(status_code=404, detail="El jugador no existe.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4001, "El jugador no existe.")
        
    async def validate_player_turn(self, playerID: int, gameID: int, websocket: Optional[WebSocket] = None):
        if self.game_repository.is_player_turn(playerID, gameID):
            return
        if websocket is None:
            raise HTTPException(status_code=403, detail="No es el turno del jugador.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4005, "No es el turno del jugador.")
        
    def validate_movement_card(self, gameID: int, request:MovementCardRequest) -> bool:
        if request.origin.posX < 0 or request.origin.posX > 5:
            raise ValueError("Origin position is out of the board")
        if request.origin.posY < 0 or request.origin.posY > 5:
            raise ValueError("Origin position is out of the board")
        if request.destination.posX < 0 or request.destination.posX > 5:
            raise ValueError("Destination position is out of the board")
        if request.destination.posY < 0 or request.destination.posY > 5:
            raise ValueError("Destination position is out of the board")
        
        movement_card = self.game_repository.get_movement_card(request.card_movementID)
        if movement_card is None:
            raise ValueError("Movement card does not exist")
        
        if movement_card.type not in self.movement_validators:
            raise ValueError("Movement card not supported")
        
        if not self.movement_validators[movement_card.type](request):
            raise HTTPException(status_code=403, detail="Movimiento inválido.")
        
        return

        

    def mov_calc(self, request:MovementCardRequest):
        deltaX = abs(request.origin.posX - request.destination.posX)
        deltaY = abs(request.origin.posY - request.destination.posY)
        return deltaX, deltaY

    def validate_mov1(self, request:MovementCardRequest) -> bool:
        deltaX, deltaY = self.mov_calc(request)
        return deltaX == 2 and deltaY == 2

    def validate_mov2(self, request:MovementCardRequest) -> bool:
        deltaX, deltaY = self.mov_calc(request)
        return deltaX == 0 and deltaY == 2

    def validate_mov3(self, request:MovementCardRequest) -> bool:
        deltaX, deltaY = self.mov_calc(request)
        return deltaX == 0 and deltaY == 1

    def validate_mov4(self, request:MovementCardRequest) -> bool:
        deltaX, deltaY = self.mov_calc(request)
        return deltaX == 1 and deltaY == 1

    def validate_mov5(self, request:MovementCardRequest) -> bool:
        up_posX_correct = (request.origin.posX - 2) == request.destination.posX
        up_posY_correct = (request.origin.posY + 1) == request.destination.posY
        up_correct = up_posX_correct and up_posY_correct

        down_posX_correct = (request.origin.posX + 2) == request.destination.posX
        down_posY_correct = (request.origin.posY - 1) == request.destination.posY
        down_correct = down_posX_correct and down_posY_correct
        return up_correct or down_correct

    def validate_mov6(self,  request:MovementCardRequest) -> bool:
        up_posX_correct = (request.origin.posX - 2) == request.destination.posX
        up_posY_correct = (request.origin.posY - 1) == request.destination.posY
        up_correct = up_posX_correct and up_posY_correct

        down_posX_correct = (request.origin.posX + 2) == request.destination.posX 
        down_posY_correct = (request.origin.posY + 1) == request.destination.posY
        down_correct = down_posX_correct and down_posY_correct
        return up_correct or down_correct

    def validate_mov7(self, request:MovementCardRequest) -> bool:
        deltaX, deltaY = self.mov_calc(request)
        return deltaX == 3 and deltaY == 0




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
