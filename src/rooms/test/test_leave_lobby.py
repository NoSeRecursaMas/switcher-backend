from src.shared.mocks import leave_room_mock, mock_db, new_mock
import pytest


def test_leave_room(new_mock, mock_db):

    player_repo_patch, room_repo_patch = leave_room_mock()

    with player_repo_patch, room_repo_patch:
        roomID = 1
        playerID = {"playerID": 1}

        reponse = new_mock.put(f"/rooms/{roomID}/leave", json=playerID)

        assert reponse.status_code == 200


def test_leave_room_player_not_in_room(new_mock, mock_db):

    player_repo_patch, room_repo_patch = leave_room_mock(player_exists=False)

    with player_repo_patch, room_repo_patch:
        roomID = 1
        playerID = {"playerID": 1}

        reponse = new_mock.put(f"/rooms/{roomID}/leave", json=playerID)

        assert reponse.status_code == 404
        assert reponse.json() == {
            "detail": "El jugador proporcionado no existe."}


def test_leave_room_room_not_found(new_mock, mock_db):

    player_repo_patch, room_repo_patch = leave_room_mock(room_exists=False)

    with player_repo_patch, room_repo_patch:
        roomID = 1
        playerID = {"playerID": 1}

        reponse = new_mock.put(f"/rooms/{roomID}/leave", json=playerID)

        assert reponse.status_code == 404
        assert reponse.json() == {"detail": "La sala proporcionada no existe."}


def test_leave_room_owner(new_mock, mock_db):

    player_repo_patch, room_repo_patch = leave_room_mock(is_owner=True)

    with player_repo_patch, room_repo_patch:
        roomID = 1
        playerID = {"playerID": 1}

        reponse = new_mock.put(f"/rooms/{roomID}/leave", json=playerID)

        assert reponse.status_code == 405
        assert reponse.json() == {
            "detail": "El propietario no puede abandonar la sala."}
