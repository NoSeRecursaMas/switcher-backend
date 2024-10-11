import random
from typing import List, Dict, Union, Optional
from src.games.config import COLORS

from fastapi import HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.games.domain.repository import GameRepository
from src.rooms.domain.repository import RoomRepository
from src.players.domain.repository import PlayerRepository


class GameServiceDomain:
    def __init__(self, game_repository: GameRepository, player_repository: PlayerRepository):
        self.game_repository = game_repository
        self.player_repository = player_repository

    @staticmethod
    def create_board() -> List[Dict[str, Union[int, str]]]:
        color_pool = 9 * COLORS
        random.shuffle(color_pool)

        board = []
        for i in range(6):
            for j in range(6):
                token = {
                    "PosX": i,
                    "PosY": j,
                    "Color": color_pool.pop()
                }
                board.append(token)

        return board

    def set_game_turn_order(self, gameID: int) -> None:
        players = self.game_repository.get_game_players(gameID)
        player_count = len(players)

        positions = list(range(1, player_count + 1))

        random.shuffle(positions)

        for player, position in zip(players, positions):
            self.player_repository.set_position(player.playerID, position)


class RepositoryValidators:
    def __init__(
        self,
        room_repository: RoomRepository,
        player_repository: Optional[PlayerRepository] = None,
    ):
        self.room_repository = room_repository
        self.player_repository = player_repository

    async def validate_room_exists(self, roomID: int, websocket: Optional[WebSocket] = None):
        if self.room_repository.get(roomID) is not None:
            return
        if websocket is None:
            raise HTTPException(status_code=404, detail="La sala no existe.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(4004, "La sala no existe.")

    async def validate_player_in_room(self, playerID: int, roomID: int, websocket: Optional[WebSocket] = None):
        if self.room_repository.is_player_in_room(playerID, roomID):
            return
        if websocket is None:
            raise HTTPException(
                status_code=403, detail="El jugador no se encuentra en la sala.")
        else:
            await websocket.accept()
            raise WebSocketDisconnect(
                4003, "El jugador no se encuentra en la sala.")

    def validate_player_is_not_owner(self, playerID: int, roomID: int):
        if self.room_repository.is_owner(playerID, roomID):
            raise HTTPException(
                status_code=405, detail="El propietario no puede abandonar la sala.")

    def validate_room_full(self, roomID: int):
        room = self.room_repository.get_public_info(roomID)
        if len(room.players) >= room.maxPlayers:
            raise HTTPException(status_code=405, detail="La sala está llena.")
