from src.games.domain.models import GameID 
from src.players.domain.models import PlayerID
from src.games.domain.repository import GameRepository
from src.games.config import COLORS
import random

class GameService:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def start_game(self, roomID: int, player : PlayerID) -> GameID:
        self.repository.create_board()