

def test_create_player(client, test_db):

    #player_data = {"playerID" : 1, "username": "mensio"}

    response = client.post("/players", json={"username": "mensio"} )

    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "mensio"}


def test_create_player_invalid_size(client, test_db):
    response = client.post("/players", json={"username": ""})
    assert response.status_code == 422
    assert (
        response.json().get("detail")[0]["msg"]
        == "El username proporcionado no cumple con los requisitos de longitud permitidos."
    )


def test_create_player_long_name(client, test_db):
    long_name = "A" * 33
    response = client.post("/players", json={"username": long_name})
    assert response.status_code == 422
    assert (
        response.json().get("detail")[0]["msg"]
        == "El username proporcionado no cumple con los requisitos de longitud permitidos."
    )


def test_create_player_non_ascii(client, test_db):
    response = client.post("/players", json={"username": "nombre_con_ñ"})
    assert response.status_code == 422
    assert response.json().get("detail")[0]["msg"] == "El username proporcionado contiene caracteres no permitidos."


def test_create_player_one_character(client, test_db):

    player_data = {"playerID" : 1, "username": "A"}

    response = client.post("/players", json=player_data)

    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "A"}


def test_create_player_with_spaces(client, test_db):

    player_data = {"playerID" : 1, "username": "S A N   T I"}

    response = client.post("/players", json=player_data)

    assert response.status_code == 201
    assert response.json() == {"playerID": 1, "username": "S A N   T I"}


def test_create_two_players_with_same_name(client, test_db):

    player_data = {"playerID" : 1, "username": "mensio"}
         
    response1 = client.post("/players", json=player_data)      

    assert response1.status_code == 201
    player1 = response1.json()
    assert player1["username"] == "mensio"

    player_data2 = {"playerID" : 2, "username": "mensio"}

    response2 = client.post("/players", json=player_data2)

    assert response2.status_code == 201
    player2 = response2.json()

    assert player1["playerID"] == 1
    assert player2["playerID"] == 2

    assert player1["playerID"] != player2["playerID"]
