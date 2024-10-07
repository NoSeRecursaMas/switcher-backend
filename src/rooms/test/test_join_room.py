# import pytest
# from src.shared.mocks import mock_db, new_mock, join_room_mock


# def test_join_room(new_mock, mock_db):
#     player_repo_patch, room_repo_patch = join_room_mock()

#     with player_repo_patch, room_repo_patch:
#         roomID = 1
#         playerID = {"playerID": 1}
#         response = new_mock.put(f"/rooms/{roomID}/join", json=playerID)

#         assert response.status_code == 200


# def test_join_room_not_exists(new_mock, mock_db):
#     player_repo_patch, room_repo_patch = join_room_mock(room_exists=False)

#     with player_repo_patch, room_repo_patch:
#         roomID = 1
#         playerID = {"playerID": 1}
#         response = new_mock.put(f"/rooms/{roomID}/join", json=playerID)

#         assert response.status_code == 404


# def test_join_room_full(new_mock, mock_db):
#     player_repo_patch, room_repo_patch = join_room_mock(full=True)

#     with player_repo_patch, room_repo_patch:
#         roomID = 1
#         playerID = {"playerID": 1}
#         response = new_mock.put(f"/rooms/{roomID}/join", json=playerID)

#         assert response.status_code == 405


# def test_join_room_player_not_exists(new_mock, mock_db):
#     player_repo_patch, room_repo_patch = join_room_mock(player_exists=False)

#     with player_repo_patch, room_repo_patch:
#         roomID = 1
#         playerID = {"playerID": 1}
#         response = new_mock.put(f"/rooms/{roomID}/join", json=playerID)

#         assert response.status_code == 404
