from typing import Optional

from fastapi import WebSocket

from src.games.domain.models import GameID
from src.games.domain.repository import GameRepositoryWS
from src.games.domain.service import GameServiceDomain
from src.games.domain.service import RepositoryValidators as GameRepositoryValidators
from src.players.domain.models import PlayerID
from src.players.domain.repository import PlayerRepository
from src.players.domain.service import RepositoryValidators as PlayerRepositoryValidators
from src.rooms.domain.repository import RoomRepositoryWS
from src.rooms.domain.service import RepositoryValidators as RoomRepositoryValidators


class GameService:
    def __init__(
        self,
        game_repository: GameRepositoryWS,
        player_repository: PlayerRepository,
        room_repository: Optional[RoomRepositoryWS] = None,
    ):
        self.game_repository = game_repository
        self.player_repository = player_repository
        self.room_repository = room_repository
        self.player_domain_service = PlayerRepositoryValidators(player_repository)
        if room_repository is not None:
            self.room_domain_service = RoomRepositoryValidators(room_repository, player_repository)
        self.game_domain_service = GameRepositoryValidators(game_repository, room_repository)

    async def start_game(self, roomID: int, playerID: PlayerID) -> GameID:
        await self.player_domain_service.validate_player_exists(playerID.playerID)
        await self.room_domain_service.validate_room_exists(roomID)
        self.room_domain_service.validate_player_is_owner(playerID.playerID, roomID)
        self.game_domain_service.validate_min_players_to_start(roomID)

        board = GameServiceDomain.create_board()

        response = self.game_repository.create(roomID, board)
        gameID = response.gameID

        self.game_repository.create_figure_cards(gameID)
        self.game_repository.create_movement_cards(gameID)

        if self.room_repository is None:
            raise ValueError("RoomRepository is required to start a game")
        game_service_domain = GameServiceDomain(self.game_repository, self.room_repository)

        game_service_domain.set_game_turn_order(gameID)

        await self.room_repository.broadcast_status_room_list()
        await self.room_repository.broadcast_start_game(roomID, gameID)

        return response

    async def connect_to_game_websocket(self, playerID: int, gameID: int, websocket: WebSocket) -> None:
        await self.player_domain_service.validate_player_exists(playerID, websocket)
        await self.game_domain_service.validate_game_exists(gameID, websocket)
        await self.game_domain_service.is_player_in_game(playerID, gameID, websocket)

        await self.game_repository.setup_connection_game(playerID, gameID, websocket)

    async def leave_game(self, gameID: int, playerID: int) -> None:
        await self.player_domain_service.validate_player_exists(playerID)
        await self.game_domain_service.validate_game_exists(gameID)
        await self.game_domain_service.is_player_in_game(playerID, gameID)

        self.game_repository.set_player_inactive(playerID, gameID)

        await self.game_repository.broadcast_status_game(gameID)

        active_players = self.game_repository.get_active_players(gameID)
        if len(active_players) == 1:
            await self.game_repository.broadcast_end_game(gameID, active_players[0].playerID)
