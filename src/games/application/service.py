from src.games.domain.models import GameID
from src.players.domain.models import PlayerID
from src.games.domain.repository import GameRepository
from src.games.domain.service import GameServiceDomain


class GameService:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    def start_game(self, roomID: int, player: PlayerID) -> GameID:

        board = GameServiceDomain.create_board()

        gameID = self.repository.create(roomID, board)

        self.repository.create_figure_cards(roomID, gameID)
        self.repository.create_movement_cards(roomID, gameID)

        return gameID
