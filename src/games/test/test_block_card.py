import json
from typing import List

import numpy as np
import pytest

from src.conftest import override_get_db
from src.games.domain.models import BoardPiece, BoardPiecePosition
from src.games.infrastructure.models import FigureCard as FigureCardDB
from src.games.infrastructure.models import Game as GameDB
from src.games.infrastructure.repository import SQLAlchemyRepository
from src.players.infrastructure.models import Player as PlayerDB
from src.rooms.infrastructure.models import PlayerRoom as PlayerRoomDB
from src.rooms.infrastructure.models import Room as RoomDB


@pytest.fixture
def create_players(test_db):
    players = [
        PlayerDB(playerID=1, username="test user"),
        PlayerDB(playerID=2, username="test user 2"),
        PlayerDB(playerID=3, username="test user 3"),
    ]
    test_db.add_all(players)
    test_db.commit()
    return players


@pytest.fixture
def create_room(test_db, create_player_room):
    room = RoomDB(roomID=1, roomName="test room", minPlayers=2, maxPlayers=4, hostID=create_player_room[0].playerID)
    test_db.add(room)
    test_db.commit()
    return room


@pytest.fixture
def create_player_room(test_db, create_players):
    player_room = [
        PlayerRoomDB(playerID=create_players[0].playerID, roomID=1, position=1),
        PlayerRoomDB(playerID=create_players[1].playerID, roomID=1, position=2),
    ]
    test_db.add_all(player_room)
    test_db.commit()
    return player_room


@pytest.fixture
def create_game(test_db, create_room):
    game = GameDB(
        roomID=create_room.roomID,
        board=json.dumps([{"posX": 0, "posY": 0, "color": "R"} for _ in range(36)]),
        posEnabledToPlay=1,
    )

    test_db.add(game)
    test_db.commit()
    return game


@pytest.fixture
def create_figure_card(test_db):
    figure_cards = [
        FigureCardDB(type="fige06", isBlocked=False, isPlayable=True, playerID=1, gameID=1),
        FigureCardDB(type="fige01", isBlocked=False, isPlayable=True, playerID=1, gameID=1),
        FigureCardDB(type="fige02", isBlocked=False, isPlayable=True, playerID=1, gameID=1),
    ]
    test_db.add_all(figure_cards)
    test_db.commit()
    return figure_cards


@pytest.fixture
def create_board_version_1():
    return json.dumps(
        [
            {"posX": 0, "posY": 0, "color": "R", "isPartial": False},
            {"posX": 0, "posY": 1, "color": "R", "isPartial": False},
            {"posX": 0, "posY": 2, "color": "R", "isPartial": False},
            {"posX": 0, "posY": 3, "color": "R", "isPartial": False},
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
            {"posX": 2, "posY": 2, "color": "R", "isPartial": False},
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
    )


@pytest.fixture
def create_board_version_2():
    return json.dumps(
        [
            {"posX": 0, "posY": 0, "color": "R", "isPartial": False},
            {"posX": 0, "posY": 1, "color": "R", "isPartial": False},
            {"posX": 0, "posY": 2, "color": "R", "isPartial": False},
            {"posX": 0, "posY": 3, "color": "R", "isPartial": False},
            {"posX": 0, "posY": 4, "color": "G", "isPartial": False},
            {"posX": 0, "posY": 5, "color": "G", "isPartial": False},
            {"posX": 1, "posY": 0, "color": "G", "isPartial": False},
            {"posX": 1, "posY": 1, "color": "G", "isPartial": False},
            {"posX": 1, "posY": 2, "color": "G", "isPartial": False},
            {"posX": 1, "posY": 3, "color": "G", "isPartial": False},
            {"posX": 1, "posY": 4, "color": "R", "isPartial": False},
            {"posX": 1, "posY": 5, "color": "G", "isPartial": False},
            {"posX": 2, "posY": 0, "color": "G", "isPartial": False},
            {"posX": 2, "posY": 1, "color": "G", "isPartial": False},
            {"posX": 2, "posY": 2, "color": "R", "isPartial": False},
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
    )


def test_figure_block(client, test_db, create_game, create_board_version_2, create_figure_card):
    game = create_game

    game.board = create_board_version_2

    figure_card = create_figure_card

    figure_card[0].type = "fige06"
    test_db.commit()

    response = client.put(
        "/games/1/block",
        json={
            "cardID": 1,
            "targetID": 1,
            "playerID": 2,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 201
    assert figure_card[0].isBlocked == True
    assert response.json() is None


def test_block_blocked_card(client, test_db, create_game, create_board_version_2):
    game = create_game

    game.board = create_board_version_2

    figure_cards = [
        FigureCardDB(type="fige06", isBlocked=False, isPlayable=True, wasBlocked=False, playerID=1, gameID=1),
        FigureCardDB(type="fige01", isBlocked=False, isPlayable=False, wasBlocked=False, playerID=1, gameID=1),
        FigureCardDB(type="fige02", isBlocked=False, isPlayable=False, wasBlocked=False, playerID=1, gameID=1),
        FigureCardDB(type="fige06", isBlocked=True, isPlayable=False, wasBlocked=False, playerID=2, gameID=1),
        FigureCardDB(type="fige03", isBlocked=False, isPlayable=False, wasBlocked=False, playerID=2, gameID=1),
        FigureCardDB(type="fige03", isBlocked=False, isPlayable=False, wasBlocked=False, playerID=2, gameID=1),
    ]

    test_db.add_all(figure_cards)
    test_db.commit()

    response = client.put(
        "/games/1/block",
        json={
            "cardID": 4,
            "playerID": 1,
            "targetID": 2,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "La carta esta bloqueada."}


def test_unblock_blocked_card(client, test_db, create_game, create_board_version_2):
    game = create_game
    game.board = create_board_version_2

    figure_cards = [
        FigureCardDB(type="fige06", isBlocked=False, isPlayable=True, wasBlocked=False, playerID=1, gameID=1),
        FigureCardDB(type="fige01", isBlocked=True, isPlayable=True, wasBlocked=False, playerID=1, gameID=1),
    ]

    test_db.add_all(figure_cards)
    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )
    test_db.refresh(figure_cards[1])
    assert response.status_code == 201
    assert response.json() is None
    assert figure_cards[1].isBlocked == False
    assert figure_cards[1].wasBlocked == True


def test_last_card_unblocked_and_skip_turn(client, test_db, create_game, create_board_version_2, create_player_room):
    game = create_game
    game.board = create_board_version_2
    players = create_player_room
    figure_cards = [
        FigureCardDB(type="fige06", isBlocked=True, isPlayable=True, wasBlocked=False, playerID=1, gameID=1),
        FigureCardDB(type="fige01", isBlocked=False, isPlayable=False, wasBlocked=False, playerID=1, gameID=1),
        FigureCardDB(type="fige02", isBlocked=False, isPlayable=False, wasBlocked=False, playerID=1, gameID=1),
        FigureCardDB(type="fige03", isBlocked=False, isPlayable=False, wasBlocked=False, playerID=1, gameID=1),
    ]
    test_db.add_all(figure_cards)
    test_db.commit()

    response = client.put(f"/games/{game.gameID}/turn", json={"playerID": players[0].playerID})
    assert response.status_code == 200
    test_db.refresh(game)
    assert game.posEnabledToPlay == 2

    cards = (
        test_db.query(FigureCardDB)
        .filter(
            FigureCardDB.gameID == game.gameID,
            FigureCardDB.playerID == players[0].playerID,
            FigureCardDB.isPlayable == True,
        )
        .all()
    )

    assert len(cards) == 1
    assert cards[0].cardID == figure_cards[0].cardID


def test_block_with_less_than_3_cards(client, test_db, create_game, create_board_version_2, create_player_room):
    game = create_game

    game.board = create_board_version_2

    figure_cards = [
        FigureCardDB(type="fige06", isBlocked=False, isPlayable=True, playerID=1, gameID=1),
        FigureCardDB(type="fige01", isBlocked=False, isPlayable=True, playerID=1, gameID=1),
    ]
    test_db.add_all(figure_cards)
    test_db.commit()

    figure_cards[0].type = "fige06"
    test_db.commit()

    response = client.put(
        "/games/1/block",
        json={
            "cardID": 1,
            "targetID": 1,
            "playerID": 2,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 403
    assert figure_cards[0].isBlocked == False
    assert response.json() == {"detail": "El jugador tiene menos de tres cartas de figura."}
