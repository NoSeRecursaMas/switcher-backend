import pytest
from src.shared.mocks import mock_db, new_mock,join_lobby_mock


def test_join_lobby(new_mock,mock_db):
    player_repo_patch, lobby_repo_patch = join_lobby_mock()

    with player_repo_patch, lobby_repo_patch:
        lobby_id = 1
        player_id = {"playerID": 1}
        response = new_mock.put(f"/rooms/{lobby_id}/join", json=player_id)

        assert response.status_code == 200

def test_join_lobby_not_exists(new_mock,mock_db):
    player_repo_patch, lobby_repo_patch = join_lobby_mock(lobby_exists=False)

    with player_repo_patch, lobby_repo_patch:
        lobby_id = 1
        player_id = {"playerID": 1}
        response = new_mock.put(f"/rooms/{lobby_id}/join", json=player_id)

        assert response.status_code == 404


def test_join_lobby_full(new_mock,mock_db):
    player_repo_patch, lobby_repo_patch = join_lobby_mock(full=True)

    with player_repo_patch, lobby_repo_patch:
        lobby_id = 1
        player_id = {"playerID": 1}
        response = new_mock.put(f"/rooms/{lobby_id}/join", json=player_id)

        assert response.status_code == 405

def test_join_lobby_player_not_exists(new_mock,mock_db):
    player_repo_patch, lobby_repo_patch = join_lobby_mock(player_exists=False)

    with player_repo_patch, lobby_repo_patch:
        lobby_id = 1
        player_id = {"playerID": 1}
        response = new_mock.put(f"/rooms/{lobby_id}/join", json=player_id)

        assert response.status_code == 404

