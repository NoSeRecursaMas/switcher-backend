from src.shared.mocks import leave_lobby_mock, mock_db, new_mock
import pytest


def test_leave_lobby(new_mock, mock_db):

    player_repo_patch, lobby_repo_patch = leave_lobby_mock()

    with player_repo_patch, lobby_repo_patch:
        lobby_id = 1
        player_id = {"playerID": 1}

        reponse = new_mock.put(f"/rooms/{lobby_id}/leave", json=player_id)

        assert reponse.status_code == 200


def test_leave_lobby_player_not_in_lobby(new_mock, mock_db):

    player_repo_patch, lobby_repo_patch = leave_lobby_mock(player_exists=False)

    with player_repo_patch, lobby_repo_patch:
        lobby_id = 1
        player_id = {"playerID": 1}

        reponse = new_mock.put(f"/rooms/{lobby_id}/leave", json=player_id)

        assert reponse.status_code == 404
        assert reponse.json() == {
            "detail": "El jugador proporcionado no existe."}


def test_leave_lobby_lobby_not_found(new_mock, mock_db):

    player_repo_patch, lobby_repo_patch = leave_lobby_mock(lobby_exists=False)

    with player_repo_patch, lobby_repo_patch:
        lobby_id = 1
        player_id = {"playerID": 1}

        reponse = new_mock.put(f"/rooms/{lobby_id}/leave", json=player_id)

        assert reponse.status_code == 404
        assert reponse.json() == {"detail": "La sala proporcionada no existe."}


def test_leave_lobby_owner(new_mock, mock_db):

    player_repo_patch, lobby_repo_patch = leave_lobby_mock(is_owner=True)

    with player_repo_patch, lobby_repo_patch:
        lobby_id = 1
        player_id = {"playerID": 1}

        reponse = new_mock.put(f"/rooms/{lobby_id}/leave", json=player_id)

        assert reponse.status_code == 405
        assert reponse.json() == {
            "detail": "El propietario no puede abandonar la sala."}
