from . import BASE_URL
import pytest, requests


def create_account(username: str): 
    payload = {"username": username, "password": f"{username}{username}1!", "email": f"{username}@gmail.com"}

    session = requests.Session()
    response = session.post(BASE_URL + "/user", json=payload)

    for c in session.cookies:
        c.secure = False

    assert response.status_code == 200, f"{response.json()}"
    assert response.json() == {"message":"Conta criada com sucesso!"}

    return {**payload, "cookies": session.cookies}


def delete_account(user: dict):
    response = requests.delete(BASE_URL + "/user", cookies=user["cookies"])

    assert response.status_code == 200
    assert response.json() == {"message":"Conta deletada com sucesso!"}


def get_games(game_name: str):
    payload = {"page": 1, "page_size": 10}

    response = requests.get(BASE_URL + f"/game/{game_name}", json=payload)
    assert response.status_code == 200

    games_list = response.json()["games"]
    game_ids_list = [(g["game_id"], g["name"]) for g in games_list]

    return game_ids_list

@pytest.fixture(scope='module')
def users():
    users = {
        "Alice": create_account("Alice"),
        "Bernardo": create_account("Bernardo"),
        "Caua": create_account("Caua"),
        "Daniela" :create_account("Daniela"),
        "Eduarda": create_account("Eduarda"),
        "Fabio": create_account("Fabio"),
        "Gabriela": create_account("Gabriela"),
        "Helio": create_account("Helio"),
        "Iara": create_account("Iara")
    }

    yield users

    for user in users.values():
        delete_account(user) 


@pytest.fixture(scope='module')
def games():
    games = {
        "mario": get_games("mario"),
        "GTA": get_games("GTA"),
        "roblox": get_games("roblox"),
    }

    return games








