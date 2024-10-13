import random

from src.games.domain.models import GameID
from src.games.domain.repository import GameRepository
from src.games.domain.service import GameServiceDomain
from src.players.domain.models import PlayerID
from src.players.domain.repository import PlayerRepository
from src.players.domain.service import RepositoryValidators as PlayerRepositoryValidators
from src.rooms.domain.repository import RoomRepository
from src.rooms.domain.service import RepositoryValidators as RoomRepositoryValidators


class GameService:
    def __init__(
        self, game_repository: GameRepository, player_repository: PlayerRepository, room_repository: RoomRepository
    ):
        self.game_repository = game_repository
        self.player_repository = player_repository
        self.room_repository = room_repository
        self.player_domain_service = PlayerRepositoryValidators(player_repository)
        self.room_domain_service = RoomRepositoryValidators(room_repository)

    async def start_game(self, roomID: int, playerID: PlayerID) -> GameID:
        await self.player_domain_service.validate_player_exists(playerID.playerID)
        await self.room_domain_service.validate_room_exists(roomID)
        self.room_domain_service.validate_player_is_owner(playerID.playerID, roomID)
        self.room_domain_service.validate_min_players_to_start(roomID)

        board = GameServiceDomain.create_board()

        gameID = self.game_repository.create(roomID, board)

        self.game_repository.create_figure_cards(roomID, gameID)
        self.game_repository.create_movement_cards(roomID, gameID)

        game_service_domain = GameServiceDomain(self.game_repository, self.room_repository)

        game_service_domain.set_game_turn_order(gameID.gameID)

        return gameID
    
    def skip_turn(self,player: PlayerID, gameID: GameID) -> None:

        game_service_domain = GameServiceDomain(self.game_repository, self.player_repository)
        self.game_service_domain.player_exists_in_game(player.playerID, gameID.gameID)
        self.game_service_domain.game_exists(gameID.gameID)
        
        self.game_repository.skip(gameID)
        self.game_repository.replacement_movement_card(gameID.gameID, player.playerID)
        self.game_repository.replacement_figure_card(gameID.gameID, player.playerID)
        

