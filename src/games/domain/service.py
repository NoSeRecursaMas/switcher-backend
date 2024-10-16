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
        pass 

    def validate_mov01(self, request:MovementCardRequest) -> bool:
        #Caso donde yo quiero mover en direccion derecha arriba
        mov_up_rightX = (request.origin.posX+2) == request.destination.posX
        mov_up_rightY = (request.origin.posY+2) == request.destination.posY 
        mov_up_right = mov_up_rightX and mov_up_rightY

        #Caso donde yo quiero mover en direccion izquierda arriba
        mov_up_leftX = (request.origin.posX-2) == request.destination.posX
        mov_up_leftY = (request.origin.posY+2) == request.destination.posY
        mov_up_left = mov_up_leftX and mov_up_leftY

        #Caso donde yo quiero mover en direccion derecha abajo
        mov_down_rightX = (request.origin.posX+2) == request.destination.posX
        mov_down_rightY = (request.origin.posY-2) == request.destination.posY
        mov_down_right = mov_down_rightX and mov_down_rightY

        #Caso donde yo quiero mover en direccion izquierda abajo
        mov_down_leftX = (request.origin.posX-2) == request.destination.posX
        mov_down_leftY = (request.origin.posY-2) == request.destination.posY
        mov_down_left = mov_down_leftX and mov_down_leftY

        return mov_up_right or mov_up_left or mov_down_right or mov_down_left

    def validate_mov02(self, request:MovementCardRequest) -> bool:
        pass

    def validate_mov03(self, request:MovementCardRequest) -> bool:
        pass

    def validate_mov04(self, request:MovementCardRequest) -> bool:
        pass

    def validate_mov05(self, request:MovementCardRequest) -> bool:
        pass

    def validate_mov06(self,  request:MovementCardRequest) -> bool:
        pass

    def validate_mov07(self, request:MovementCardRequest) -> bool:
        pass



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
