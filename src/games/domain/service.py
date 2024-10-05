import json
import random
from src.games.config import COLORS

class GameServiceDomain:
    
    def create_board() -> json:
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
        
        board_json = json.dumps(board)
        return board_json