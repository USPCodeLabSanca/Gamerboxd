from .utils import *


def _create_account_by_username(username: str):
    """Insere uma conta no DB pelo username"""

    payload = {"username": username, "password": f"{username}{username}1!", "email": f"{username}@gmail.com"}

    session = requests.Session()
    response = session.post(BASE_URL_USERS, json=payload)

    for c in session.cookies:
        c.secure = False

    response_json = response.json()

    assert response.status_code == 200, response_json
    assert "message" in response_json.keys()
    assert response_json["message"] == "Conta criada com sucesso!"
    assert "id" in response_json.keys()

    return BaseUser(
        user_id = response_json["id"],
        username=payload["username"],
        pwd=payload["password"],
        email=payload["email"],
        cookies=session.cookies
    )


def _delete_account(user: BaseUser):
    """Deleta uma conta do DB"""

    response = requests.delete(BASE_URL_USERS, cookies=user.cookies)

    assert response.status_code == 200
    assert response.json() == {"message":"Conta deletada com sucesso!"}


@pytest.fixture(scope='module')
def users():
    """Conjunto de usuários para testes"""

    users = {
        "Alice": _create_account_by_username("Alice"),
        "Bernardo": _create_account_by_username("Bernardo"),
        "Caua": _create_account_by_username("Caua"),
        "Daniela" :_create_account_by_username("Daniela"),
    }

    yield users

    for user in users.values():
        _delete_account(user) 


@pytest.fixture(scope='session')
def games():
    """Conjunto de games para testes"""

    def _get_games(game_name: str):
        """Pega 10 jogos relacionados a um nome na API rawg"""

        url = BASE_URL_GAMES + f"/{game_name}" + "?detail=false&page=1&page_size=10"

        response = requests.get(url)
        assert response.status_code == 200, response.json()

        games_list = response.json()["games"]
        game_ids_list = [g["game_id"] for g in games_list]

        return game_ids_list

    games = {
        "mario": _get_games("mario"),
        "GTA": _get_games("GTA"),
        "roblox": _get_games("roblox"),
    }

    return games


@pytest.fixture
def follow_request():
    """Faz o request para seguir um usuário
    cleanup = True significa que vai apagar do DB depois"""

    responses = []

    # Tenta inserir o block no DB
    def _follow(atv: BaseUser, pas: BaseUser, cleanup: bool = True):
        target, cookies = pas.user_id, atv.cookies
        post_resp = requests.post(BASE_URL_USERS + f"/follow/{target}", cookies=cookies)
        if cleanup:
            assert post_resp.status_code == 200, post_resp.json()
            responses.append({"target": target, "cookies": cookies})
        return post_resp

    yield _follow

    # Faz o cleanup
    for r in responses:
        target, cookies = r["target"], r["cookies"]
        del_resp = requests.delete(BASE_URL_USERS + f"/follow/{target}", cookies=cookies)
        assert del_resp.status_code == 200, del_resp.json()


@pytest.fixture
def unfollow_request():
    """Faz o request para desseguir um usuário"""

    # Tenta deletar o block do DB
    def _unfollow_request(atv: BaseUser, pas: BaseUser):
        target, cookies = pas.user_id, atv.cookies
        return requests.delete(BASE_URL_USERS + f"/follow/{target}", cookies=cookies)

    return _unfollow_request


@pytest.fixture
def block_request():
    """Faz o request para bloquear um usuário. 
    cleanup = True significa que vai apagar do DB depois"""

    responses = []

    # Tenta inserir o block no DB
    def _block_request(atv: BaseUser, pas: BaseUser, cleanup: bool = True):
        target, cookies = pas.user_id, atv.cookies
        block_resp = requests.post(BASE_URL_USERS + f"/block/{target}", cookies=cookies)

        if cleanup:
            assert block_resp.status_code == 200, block_resp.json()
            responses.append({"target": target, "cookies": cookies})

        return block_resp

    yield _block_request

    # Faz o cleanup
    for r in responses:
        target, cookies = r["target"], r["cookies"]
        del_resp = requests.delete(BASE_URL_USERS + f"/block/{target}", cookies=cookies)
        assert del_resp.status_code == 200


@pytest.fixture
def unblock_request():
    """Faz o request para desbloquear um usuário"""

    # Tenta deletar o block do DB
    def _unblock_request(atv: BaseUser, pas: BaseUser):
        target, cookies = pas.user_id, atv.cookies
        return requests.delete(BASE_URL_USERS + f"/block/{target}", cookies=cookies)

    return _unblock_request


@pytest.fixture
def create_account():
    """Cria uma conta no DB
    cleanup = True significa que vai apagar do DB depois"""

    responses = []

    def _create_account(username: str, cleanup: bool):
        account = _create_account_by_username(username)
        if cleanup:
            responses.append(account)
        return account

    yield _create_account

    for resp in responses:
        _delete_account(resp)



