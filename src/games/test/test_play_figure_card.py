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
        prohibitedColor="Y",
        posEnabledToPlay=1,
    )

    test_db.add(game)
    test_db.commit()

    return game


@pytest.fixture
def create_figure_card(test_db):
    figure_cards = [
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


@pytest.fixture
def create_board_version_3():
    return json.dumps(
        [
            {"posX": 0, "posY": 0, "color": "Y", "isPartial": False},
            {"posX": 0, "posY": 1, "color": "Y", "isPartial": False},
            {"posX": 0, "posY": 2, "color": "Y", "isPartial": False},
            {"posX": 0, "posY": 3, "color": "Y", "isPartial": False},
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
            {"posX": 2, "posY": 2, "color": "Y", "isPartial": False},
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


def test_play_figure_card(client, test_db, create_game, create_board_version_1, create_figure_card):
    game = create_game

    game.board = create_board_version_1

    figure_card = create_figure_card

    figure_card[0].type = "fige06"
    test_db.commit()

    game_from_db = test_db.get(GameDB, game.gameID)

    assert game_from_db.prohibitedColor == "Y"

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    test_db.refresh(game)
    # no se actualiza el color prohibido

    assert response.status_code == 201
    assert game_from_db.prohibitedColor == "R"
    assert response.json() is None


def test_play_figure_card_corner_same_color(client, test_db, create_game, create_board_version_2, create_figure_card):
    game = create_game

    game.board = create_board_version_2

    figure_card = create_figure_card

    figure_card[0].type = "fige06"
    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 201
    assert response.json() is None


def test_figure_card_is_not_the_player(client, test_db, create_game, create_figure_card, create_board_version_1):
    game = create_game
    game.board = create_board_version_1

    figure_card = create_figure_card

    figure_card[0].playerID = 2
    figure_card[0].type = "fige06"
    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "La carta no pertenece al jugador."}


def test_figure_not_match_card(client, test_db, create_game, create_board_version_1, create_figure_card):
    game = create_game

    game.board = create_board_version_1

    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "La figura no coincide con la carta."}


def test_figure_card_diffent_color(client, test_db, create_game, create_board_version_1, create_figure_card):
    game = create_game

    game.board = create_board_version_1

    figure_card = create_figure_card

    figure_card[0].type = "fige06"
    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 1, "posY": 0}, {"posX": 2, "posY": 0}, {"posX": 3, "posY": 0}],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "La figura debe ser del mismo color."}


def test_figure_card_is_empty(client, test_db, create_game, create_board_version_1, create_figure_card):
    game = create_game

    game.board = create_board_version_1

    figure_card = create_figure_card

    figure_card[0].type = "fige06"
    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={"cardID": 1, "playerID": 1, "figure": []},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "La figura no puede estar vacía."}


def test_figure_card_border_invalid(client, test_db, create_game, create_board_version_1, create_figure_card):
    game = create_game

    game.board = create_board_version_1

    figure_card = create_figure_card

    figure_card[0].type = "fige06"
    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 5, "posY": 0}, {"posX": 5, "posY": 1}, {"posX": 5, "posY": 2}, {"posX": 5, "posY": 3}],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "La figura tiene una ficha adyacente del mismo color."}


def test_figure_card_separated_by_space(client, test_db, create_game, create_board_version_1, create_figure_card):
    game = create_game

    game.board = create_board_version_1

    figure_card = create_figure_card

    figure_card[0].type = "fige06"
    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 2, "posY": 0}, {"posX": 2, "posY": 1}, {"posX": 2, "posY": 3}, {"posX": 2, "posY": 4}],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "La figura no coincide con la carta."}


def test_figure_card_dont_exists(client, test_db, create_game, create_board_version_1, create_figure_card):
    game = create_game

    game.board = create_board_version_1

    figure_card = create_figure_card

    figure_card[0].cardID = 3

    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "La carta no existe en la partida."}


def test_figure_card_dont_exists_in_game(client, test_db, create_game, create_board_version_1, create_figure_card):
    game = create_game

    game.board = create_board_version_1

    figure_card = create_figure_card

    figure_card[0].gameID = 2

    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "La carta no existe en la partida."}


def test_figure_not_in_board(client, test_db, create_game, create_board_version_1, create_figure_card):
    game = create_game

    game.board = create_board_version_1

    figure_card = create_figure_card

    figure_card[0].type = "fig05"
    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [
                {"posX": 0, "posY": 0},
                {"posX": 0, "posY": 1},
                {"posX": 0, "posY": 2},
                {"posX": 0, "posY": 3},
                {"posX": 0, "posY": 4},
            ],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "La figura debe ser del mismo color."}


def test_not_player_turn(client, test_db, create_game, create_board_version_1, create_figure_card):
    game = create_game

    game.board = create_board_version_1

    figure_card = create_figure_card

    figure_card[0].type = "fige06"
    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 2,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "No es el turno del jugador."}


def test_player_not_in_game(client, test_db, create_game, create_board_version_1):
    game = create_game

    game.board = create_board_version_1

    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 3,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "El jugador no se encuentra en el juego."}


def test_game_not_exists(client, test_db, create_game, create_board_version_1):
    game = create_game

    game.board = create_board_version_1

    test_db.commit()

    response = client.post(
        "/games/2/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "El juego no existe."}


def test_player_not_exists(client, test_db, create_game, create_board_version_1):
    game = create_game

    game.board = create_board_version_1

    test_db.commit()

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 4,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "El jugador no existe."}


def test_play_figure_card_prohibited_color(client, test_db, create_game, create_board_version_3, create_figure_card):
    game = create_game

    game.board = create_board_version_3

    figure_card = create_figure_card

    figure_card[0].type = "fige06"
    test_db.commit()

    game_from_db = test_db.get(GameDB, game.gameID)

    assert game_from_db.prohibitedColor == "Y"

    response = client.post(
        "/games/1/figure",
        json={
            "cardID": 1,
            "playerID": 1,
            "figure": [{"posX": 0, "posY": 0}, {"posX": 0, "posY": 1}, {"posX": 0, "posY": 2}, {"posX": 0, "posY": 3}],
        },
    )
    test_db.refresh(game)

    assert response.status_code == 403
    assert game_from_db.prohibitedColor == "Y"
    assert response.json() == {"detail": "La figura no puede ser del color prohibido."}
