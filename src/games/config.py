from src.games.domain.service import RepositoryValidators as GameRepositoryValidators




COLORS = ["R", "G", "B", "Y"]

WHITE_CARDS_AMOUNT = [18 * 2, 12 * 2, 9 * 2]

BLUE_CARDS_AMOUNT = [7 * 2, 4 * 2, 3 * 2]

MOVEMENT_CARDS_AMOUNT = [24, 16, 12]


WHITE_CARDS = [f"fig{str(i).zfill(2)}" for i in range(1, 19)]
BLUE_CARDS = [f"fige{str(i).zfill(2)}" for i in range(1, 8)]


MOVEMENT_CARDS = [f"mov{str(i).zfill(2)}" for i in range(1, 8)]
