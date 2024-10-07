from typing import List, Dict, Union
import random
from src.games.config import COLORS

class GameServiceDomain:
    
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
    

