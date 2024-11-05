from typing import List, Optional
import logging
from fastapi import WebSocket

from src.games.domain.models import BoardPiecePosition, GameID, MovementCardRequest
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

    async def skip_turn(self, playerID: int, gameID: int) -> None:
        await self.player_domain_service.validate_player_exists(playerID)
        await self.game_domain_service.validate_game_exists(gameID)
        await self.game_domain_service.is_player_in_game(playerID, gameID)

        self.game_domain_service.validate_is_player_turn(playerID, gameID)

        self.game_repository.skip(gameID)
        self.game_repository.replacement_movement_card(gameID, playerID)
        self.game_repository.replacement_figure_card(gameID, playerID)
        self.game_repository.clean_partial_movements(gameID)
        await self.game_repository.broadcast_status_game(gameID)

    async def connect_to_game_websocket(self, playerID: int, gameID: int, websocket: WebSocket) -> None:
        await self.player_domain_service.validate_player_exists(playerID, websocket)
        await self.game_domain_service.validate_game_exists(gameID, websocket)
        await self.game_domain_service.is_player_in_game(playerID, gameID, websocket)

        await self.game_repository.setup_connection_game(playerID, gameID, websocket)

    async def play_movement_card(self, gameID: int, request: MovementCardRequest) -> None:
        await self.game_domain_service.validate_game_exists(gameID)
        await self.game_domain_service.validate_player_turn(request.playerID, gameID)
        await self.game_domain_service.is_player_in_game(request.playerID, gameID)
        await self.game_domain_service.validate_game_exists(gameID)
        self.game_domain_service.card_exists(request.cardID)
        self.game_domain_service.has_movement_card(request.playerID, request.cardID)
        self.game_domain_service.validate_movement_card(request)
        self.game_domain_service.validate_card_is_partial_movement(gameID, request.cardID)
        self.game_repository.play_movement(
            gameID,
            card_id=request.cardID,
            originX=request.origin.posX,
            originY=request.origin.posY,
            destinationX=request.destination.posX,
            destinationY=request.destination.posY,
        )
        await self.game_repository.broadcast_status_game(gameID)

    async def delete_partial_movement(self, gameID: int, playerID: int) -> None:
        await self.game_domain_service.validate_game_exists(gameID)
        await self.game_domain_service.validate_player_turn(playerID, gameID)
        await self.game_domain_service.validate_game_exists(gameID)
        await self.game_domain_service.is_player_in_game(playerID, gameID)
        self.game_domain_service.partial_movement_exists(gameID)
        self.game_repository.delete_partial_movement(gameID)
        await self.game_repository.broadcast_status_game(gameID)

    async def leave_game(self, gameID: int, playerID: int) -> None:
        await self.player_domain_service.validate_player_exists(playerID)
        await self.game_domain_service.validate_game_exists(gameID)
        await self.game_domain_service.is_player_in_game(playerID, gameID)

        self.game_repository.set_player_inactive(playerID, gameID)
        await self.game_repository.remove_player(playerID, gameID)

        active_players = self.game_repository.get_active_players(gameID)
        if len(active_players) == 1:
            await self.game_repository.broadcast_end_game(gameID, active_players[0].playerID)
            self.game_repository.delete_and_clean(gameID)
        else:
            await self.game_repository.broadcast_status_game(gameID)

    async def block_figure(self, gameID: int, playerID: int, targetID: int, cardID: int, figure: List[BoardPiecePosition]):
        await self.player_domain_service.validate_player_exists(playerID)
        await self.game_domain_service.validate_game_exists(gameID)
        await self.game_domain_service.is_player_in_game(playerID, gameID)
        self.game_domain_service.validate_is_player_turn(playerID, gameID)

        self.game_domain_service.validate_figure_card_exists(gameID, cardID)
        self.game_domain_service.validate_figure_card_belongs_to_player(targetID, cardID)
        self.game_domain_service.validate_figure_is_empty(figure)
        self.game_domain_service.validate_figure_matches_board(gameID, figure)
        self.game_domain_service.validate_figure_matches_card(cardID, figure)
        self.game_domain_service.validate_figure_border_validity(gameID, figure)

        self.game_domain_service.validate_card_is_not_blocked(cardID)

        self.game_repository.block_managment(gameID, cardID)
        self.game_repository.desvinculate_partial_movement_cards(gameID)
        self.game_repository.set_partial_movements_to_empty(gameID)

        await self.game_repository.broadcast_status_game(gameID)

    async def play_figure(self, gameID: int, playerID: int, figureID: int, figure: List[BoardPiecePosition]) -> None:
        logging.debug(f"Validating player {playerID}, game {gameID}, and figure {figureID}.")

        await self.player_domain_service.validate_player_exists(playerID)
        await self.game_domain_service.validate_game_exists(gameID)
        await self.game_domain_service.is_player_in_game(playerID, gameID)
        self.game_domain_service.validate_is_player_turn(playerID, gameID)

        self.game_domain_service.validate_figure_card_exists(gameID, figureID)
        self.game_domain_service.validate_figure_card_belongs_to_player(playerID, figureID)
        self.game_domain_service.validate_figure_is_empty(figure)
        self.game_domain_service.validate_figure_matches_board(gameID, figure)
        self.game_domain_service.validate_figure_matches_card(figureID, figure)
        self.game_domain_service.validate_figure_border_validity(gameID, figure)

        self.game_repository.play_figure(figureID)
        self.game_repository.desvinculate_partial_movement_cards(gameID)
        self.game_repository.set_partial_movements_to_empty(gameID)

        blockedcardID = self.game_repository.get_blocked_card(gameID, playerID)
        
        if blockedcardID is not None and self.game_repository.is_blocked_and_last_card(gameID, blockedcardID):
            self.game_repository.unblock_managment(gameID, blockedcardID)

        await self.game_repository.broadcast_status_game(gameID)
