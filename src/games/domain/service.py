import random
from typing import List, Dict, Union
from src.games.config import COLORS
from src.games.domain.repository import GameRepository
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
        players =  self.game_repository.get_game_players(gameID)
        player_count = len(players)
    
        positions = list(range(1, player_count + 1))
    
        random.shuffle(positions)
    
        for player, position in zip(players, positions):
            self.player_repository.set_position(player.playerID, position)
            
        

