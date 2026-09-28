from . import BASE_URL
import pytest, requests


def create_account(username: str):
    """Insere uma conta no DB"""

    payload = {"username": username, "password": f"{username}{username}1!", "email": f"{username}@gmail.com"}

    session = requests.Session()
    response = session.post(BASE_URL + "/user", json=payload)

    for c in session.cookies:
        c.secure = False

    assert response.status_code == 200, f"{response.json()}"
    assert response.json() == {"message":"Conta criada com sucesso!"}

    return {**payload, "cookies": session.cookies}


def delete_account(user: dict):
    """Deleta uma conta do DB"""

    response = requests.delete(BASE_URL + "/user", cookies=user["cookies"])

    assert response.status_code == 200
    assert response.json() == {"message":"Conta deletada com sucesso!"}


def get_games(game_name: str):
    """Pega 10 jogos relacionados a um nome na API rawg"""

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


@pytest.fixture
def follow():
    """Faz um usuário seguir o outro. cleanup = True significa que vai apagar do DB depois"""
    response = []

    def _follow(atv: dict, pas: dict, cleanup: bool):
        target, cookies = pas["username"], atv["cookies"]
        post_resp = requests.post(f"{BASE_URL}/user/follow/{target}", cookies=cookies)
        response.append({"cleanup": cleanup, "response": post_resp, "username": target, "cookies": cookies})
        return post_resp

    yield _follow

    post_resp = response[0]

    if (post_resp["cleanup"] == True) and (post_resp["response"].status_code == 200):
        target, cookies = post_resp["username"], post_resp["cookies"]
        del_resp = requests.delete(f"{BASE_URL}/user/follow/{target}", cookies=cookies)
        assert del_resp.status_code == 200


@pytest.fixture
def unfollow():
    """Faz um usuário desseguir o outro. setup = True significa que vai inserir no DB antes"""

    def _unfollow(atv: dict, pas: dict, setup: bool):
        target, cookies = pas["username"], atv["cookies"]
        if setup == True:
            post_resp = requests.post(f"{BASE_URL}/user/follow/{target}", cookies=cookies)
            assert post_resp.status_code == 200

        return requests.delete(f"{BASE_URL}/user/follow/{target}", cookies=cookies)

    return _unfollow


@pytest.fixture
def block():
    """Faz um usuário bloquear o outro. cleanup = True significa que vai apagar do DB depois"""
    response = []

    def _block(atv: dict, pas: dict, cleanup: bool):
        target, cookies = pas["username"], atv["cookies"]
        post_resp = requests.post(f"{BASE_URL}/user/block/{target}", cookies=cookies)
        response.append({"cleanup": cleanup, "response": post_resp, "username": target, "cookies": cookies})
        return post_resp

    yield _block

    post_resp = response[0]

    if (post_resp["cleanup"] == True) and (post_resp["response"].status_code == 200):
        target, cookies = post_resp["username"], post_resp["cookies"]
        del_resp = requests.delete(f"{BASE_URL}/user/block/{target}", cookies=cookies)
        assert del_resp.status_code == 200


@pytest.fixture
def unblock():
    """Faz um usuário desbloquear o outro. setup = True significa que vai inserir no DB antes"""

    def _unblock(atv: dict, pas: dict, setup: bool):
        target, cookies = pas["username"], atv["cookies"]
        if setup == True:
            post_resp = requests.post(f"{BASE_URL}/user/block/{target}", cookies=cookies)
            assert post_resp.status_code == 200

        return requests.delete(f"{BASE_URL}/user/block/{target}", cookies=cookies)

    return _unblock




