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


def test_get_available_figures(game_logic: SQLAlchemyRepository):
    board = [
        {"posX": 0, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 5, "color": "G", "isPartial": False},
    ]

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    prohibited_color = "G"
    figures = game_logic.get_available_figures(prohibited_color, board_pieces)
    assert len(figures) == 1
    assert figures == [
        [
            BoardPiecePosition(posX=4, posY=3),
            BoardPiecePosition(posX=3, posY=4),
            BoardPiecePosition(posX=4, posY=4),
            BoardPiecePosition(posX=5, posY=4),
        ]
    ]


def test_get_available_figures_2_glued_diferent_color(game_logic: SQLAlchemyRepository):
    board = [
        {"posX": 0, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 3, "color": "B", "isPartial": False},
        {"posX": 1, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 2, "color": "B", "isPartial": False},
        {"posX": 2, "posY": 3, "color": "B", "isPartial": False},
        {"posX": 2, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 2, "color": "B", "isPartial": False},
        {"posX": 3, "posY": 3, "color": "B", "isPartial": False},
        {"posX": 3, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 5, "color": "G", "isPartial": False},
    ]

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    prohibited_color = "G"
    figures = game_logic.get_available_figures(prohibited_color, board_pieces)
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
            BoardPiecePosition(posX=1, posY=3),
            BoardPiecePosition(posX=2, posY=3),
            BoardPiecePosition(posX=3, posY=3),
        ],
    ]


def test_get_available_figure_rotational_symmetry(game_logic: SQLAlchemyRepository):
    board = [
        {"posX": 0, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 0, "color": "R", "isPartial": False},
        {"posX": 2, "posY": 1, "color": "R", "isPartial": False},
        {"posX": 2, "posY": 2, "color": "R", "isPartial": False},
        {"posX": 2, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 2, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 5, "color": "G", "isPartial": False},
    ]

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    prohibited_color = "G"
    figures = game_logic.get_available_figures(prohibited_color, board_pieces)
    assert len(figures) == 1
    assert figures == [
        [
            BoardPiecePosition(posX=2, posY=0),
            BoardPiecePosition(posX=2, posY=1),
            BoardPiecePosition(posX=2, posY=2),
            BoardPiecePosition(posX=2, posY=3),
        ]
    ]


def test_figures_on_board_edges(game_logic: SQLAlchemyRepository):
    board = [
        {"posX": 0, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 2, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 5, "color": "R", "isPartial": False},
    ]

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    prohibited_color = "G"
    figures = game_logic.get_available_figures(prohibited_color, board_pieces)
    assert len(figures) == 1
    assert figures == [
        [
            BoardPiecePosition(posX=5, posY=2),
            BoardPiecePosition(posX=5, posY=3),
            BoardPiecePosition(posX=5, posY=4),
            BoardPiecePosition(posX=5, posY=5),
        ]
    ]


def test_overlapping_figures(game_logic: SQLAlchemyRepository):
    board = [
        {"posX": 0, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 2, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 2, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 5, "color": "R", "isPartial": False},
    ]

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    prohibited_color = "G"
    figures = game_logic.get_available_figures(prohibited_color, board_pieces)
    assert len(figures) == 0
    assert figures == []


def test_get_available_figures_2_glued_same_color(game_logic: SQLAlchemyRepository):
    board = [
        {"posX": 0, "posY": 0, "color": "R", "isPartial": False},
        {"posX": 0, "posY": 1, "color": "R", "isPartial": False},
        {"posX": 0, "posY": 2, "color": "R", "isPartial": False},
        {"posX": 0, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 0, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 0, "color": "R", "isPartial": False},
        {"posX": 1, "posY": 1, "color": "R", "isPartial": False},
        {"posX": 1, "posY": 2, "color": "R", "isPartial": False},
        {"posX": 1, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 1, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 5, "color": "G", "isPartial": False},
    ]

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    prohibited_color = "G"
    figures = game_logic.get_available_figures(prohibited_color, board_pieces)
    assert len(figures) == 0
    assert figures == []


def test_no_available_figures(game_logic: SQLAlchemyRepository):
    board = [{"posX": i, "posY": j, "color": "G", "isPartial": False} for i in range(6) for j in range(6)]

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    prohibited_color = "G"
    figures = game_logic.get_available_figures(prohibited_color, board_pieces)
    assert len(figures) == 0
    assert figures == []


def test_get_one_figure_prohibited_color(game_logic: SQLAlchemyRepository):
    board = [
        {"posX": 0, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 0, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 3, "color": "B", "isPartial": False},
        {"posX": 1, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 1, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 2, "color": "B", "isPartial": False},
        {"posX": 2, "posY": 3, "color": "B", "isPartial": False},
        {"posX": 2, "posY": 4, "color": "G", "isPartial": False},
        {"posX": 2, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 3, "posY": 2, "color": "B", "isPartial": False},
        {"posX": 3, "posY": 3, "color": "B", "isPartial": False},
        {"posX": 3, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 3, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 4, "posY": 3, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 4, "posY": 5, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 0, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 1, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 2, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 3, "color": "G", "isPartial": False},
        {"posX": 5, "posY": 4, "color": "R", "isPartial": False},
        {"posX": 5, "posY": 5, "color": "G", "isPartial": False},
    ]

    board_pieces: List[BoardPiece] = [BoardPiece(**piece) for piece in board]

    prohibited_color = "B"
    figures = game_logic.get_available_figures(prohibited_color, board_pieces)
    assert len(figures) == 1
    assert figures == [
        [
            BoardPiecePosition(posX=4, posY=3),
            BoardPiecePosition(posX=3, posY=4),
            BoardPiecePosition(posX=4, posY=4),
            BoardPiecePosition(posX=5, posY=4),
        ],
    ]
