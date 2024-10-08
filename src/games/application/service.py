from src.games.domain.models import GameID
from src.players.domain.models import PlayerID
from src.games.domain.repository import GameRepository
from src.games.domain.service import GameServiceDomain
from src.players.domain.repository import PlayerRepository
import random


class GameService:
    def __init__(self, game_repository: GameRepository, player_repository: PlayerRepository):
        self.game_repository = game_repository
        self.player_repository = player_repository

    def start_game(self, roomID: int, player: PlayerID) -> GameID:

        board = GameServiceDomain.create_board()

        gameID = self.game_repository.create(roomID, board)
        
        self.game_repository.create_figure_cards(roomID, gameID)
        self.game_repository.create_movement_cards(roomID, gameID)

        game_service_domain = GameServiceDomain(self.game_repository, self.player_repository)
        game_service_domain.set_game_turn_order(gameID.gameID)

        return gameID
    
    
    

