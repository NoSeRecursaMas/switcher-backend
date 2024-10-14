import random
from typing import Dict, List, Optional, Union

from fastapi import HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.games.config import COLORS
from src.games.domain.repository import GameRepository
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

    async def validate_game_exists(self, gameID: int, websocket: Optional[WebSocket] = None):
        if self.game_repository.get(gameID) is not None:
            return
        if websocket is None:
            raise HTTPException(status_code=404, detail="El juego no existe.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4004, "El juego no existe.")

    async def is_player_in_game(self, gameID: int, playerID: int, websocket: Optional[WebSocket] = None):
        if self.game_repository.is_player_in_game(gameID, playerID):
            return
        if websocket is None:
            raise HTTPException(status_code=403, detail="El jugador no se encuentra en el juego.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4003, "El jugador no se encuentra en el juego.")


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
