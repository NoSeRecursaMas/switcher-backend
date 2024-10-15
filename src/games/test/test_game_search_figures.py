import json
from typing import List

import numpy as np
import pytest

from src.conftest import override_get_db
from src.games.domain.models import BoardPiece, BoardPiecePosition
from src.games.infrastructure.repository import SQLAlchemyRepository


@pytest.fixture
def game_logic():
    db = next(override_get_db())
    return SQLAlchemyRepository(db)


def test_get_available_figures(game_logic):
    board = [
        {"posX": 0, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 1, "color": "Y", "isPartial": False},
        {"posX": 0, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 4, "color": "B", "isPartial": False},
        {"posX": 0, "posY": 5, "color": "Y", "isPartial": False},
        {"posX": 1, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 1, "color": "B", "isPartial": False},
        {"posX": 1, "posY": 2, "color": "B", "isPartial": False},
        {"posX": 1, "posY": 3, "color": "Y", "isPartial": False},
        {"posX": 1, "posY": 4, "color": "B", "isPartial": False},
        {"posX": 1, "posY": 5, "color": "Y", "isPartial": False},
        {"posX": 2, "posY": 0, "color": "Y", "isPartial": False},
        {"posX": 2, "posY": 1, "color": "Y", "isPartial": False},
        {"posX": 2, "posY": 2, "color": "R", "isPartial": False},
        {"posX": 2, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 2, "posY": 4, "color": "B", "isPartial": False},
        {"posX": 2, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 0, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 1, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 2, "color": "B", "isPartial": False},
        {"posX": 3, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 5, "color": "Y", "isPartial": False},
        {"posX": 4, "posY": 0, "color": "Y", "isPartial": False},
        {"posX": 4, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 2, "color": "Y", "isPartial": False},
        {"posX": 4, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 0, "color": "Y", "isPartial": False},
        {"posX": 5, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 2, "color": "B", "isPartial": False},
        {"posX": 5, "posY": 3, "color": "B", "isPartial": False},
        {"posX": 5, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 5, "color": "G", "isPartial": False},
    ]

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    figures = game_logic.get_available_figures(board_pieces)
    assert len(figures) == 1
    assert figures == [
        [
            BoardPiecePosition(posX=4, posY=3),
            BoardPiecePosition(posX=3, posY=4),
            BoardPiecePosition(posX=4, posY=4),
            BoardPiecePosition(posX=5, posY=4),
        ]
    ]


def test_get_available_figures_2(game_logic):
    board = [
        {"posX": 0, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 1, "color": "Y", "isPartial": False},
        {"posX": 0, "posY": 2, "color": "R", "isPartial": False},
        {"posX": 0, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 4, "color": "B", "isPartial": False},
        {"posX": 0, "posY": 5, "color": "Y", "isPartial": False},
        {"posX": 1, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 1, "color": "B", "isPartial": False},
        {"posX": 1, "posY": 2, "color": "B", "isPartial": False},
        {"posX": 1, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 4, "color": "B", "isPartial": False},
        {"posX": 1, "posY": 5, "color": "Y", "isPartial": False},
        {"posX": 2, "posY": 0, "color": "Y", "isPartial": False},
        {"posX": 2, "posY": 1, "color": "Y", "isPartial": False},
        {"posX": 2, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 4, "color": "B", "isPartial": False},
        {"posX": 2, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 0, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 1, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 5, "color": "Y", "isPartial": False},
        {"posX": 4, "posY": 0, "color": "Y", "isPartial": False},
        {"posX": 4, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 2, "color": "Y", "isPartial": False},
        {"posX": 4, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 0, "color": "Y", "isPartial": False},
        {"posX": 5, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 2, "color": "B", "isPartial": False},
        {"posX": 5, "posY": 3, "color": "B", "isPartial": False},
        {"posX": 5, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 5, "color": "G", "isPartial": False},
    ]

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    figures = game_logic.get_available_figures(board_pieces)
    assert len(figures) == 2
    assert figures == [
        [
            BoardPiecePosition(posX=4, posY=3),
            BoardPiecePosition(posX=3, posY=4),
            BoardPiecePosition(posX=4, posY=4),
            BoardPiecePosition(posX=5, posY=4),
        ],
        [
            BoardPiecePosition(posX=2, posY=2),
            BoardPiecePosition(posX=3, posY=2),
            BoardPiecePosition(posX=0, posY=3),
            BoardPiecePosition(posX=1, posY=3),
            BoardPiecePosition(posX=2, posY=3),
            BoardPiecePosition(posX=3, posY=3),
        ],
    ]


def test_no_available_figures(game_logic):
    board = [
        {"posX": 0, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 1, "color": "Y", "isPartial": False},
        {"posX": 0, "posY": 2, "color": "R", "isPartial": False},
        {"posX": 0, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 4, "color": "B", "isPartial": False},
        {"posX": 0, "posY": 5, "color": "Y", "isPartial": False},
        {"posX": 1, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 1, "color": "B", "isPartial": False},
        {"posX": 1, "posY": 2, "color": "R", "isPartial": False},
        {"posX": 1, "posY": 3, "color": "Y", "isPartial": False},
        {"posX": 1, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 5, "color": "B", "isPartial": False},
        {"posX": 2, "posY": 0, "color": "Y", "isPartial": False},
        {"posX": 2, "posY": 1, "color": "R", "isPartial": False},
        {"posX": 2, "posY": 2, "color": "B", "isPartial": False},
        {"posX": 2, "posY": 3, "color": "Y", "isPartial": False},
        {"posX": 2, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 5, "color": "B", "isPartial": False},
        {"posX": 3, "posY": 0, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 2, "color": "B", "isPartial": False},
        {"posX": 3, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 4, "color": "Y", "isPartial": False},
        {"posX": 3, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 0, "color": "B", "isPartial": False},
        {"posX": 4, "posY": 1, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 3, "color": "Y", "isPartial": False},
        {"posX": 4, "posY": 4, "color": "B", "isPartial": False},
        {"posX": 4, "posY": 5, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 0, "color": "Y", "isPartial": False},
        {"posX": 5, "posY": 1, "color": "B", "isPartial": False},
        {"posX": 5, "posY": 2, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 4, "color": "B", "isPartial": False},
        {"posX": 5, "posY": 5, "color": "Y", "isPartial": False},
    ]

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    figures = game_logic.get_available_figures(board_pieces)
    assert len(figures) == 0


def test_get_available_figures_empty_board(game_logic):
    board = []

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    figures = game_logic.get_available_figures(board_pieces)
    assert len(figures) == 0
    assert figures == []


def test_get_available_figures_single_color(game_logic):
    board = [{"posX": i, "posY": j, "color": "R", "isPartial": False} for i in range(6) for j in range(6)]
    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    figures = game_logic.get_available_figures(board_pieces)
    assert len(figures) == 0
