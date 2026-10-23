from .utils import *


@pytest.fixture
def create_list():
    """Insere uma lista no DB
    se cleanup == True, vai remover do DB depois que a função teste rodar"""

    responses = []

    # Tenta inserir no DB
    def _create_list(user: BaseUser, list_name: str = None, privacy: int = Clearence.ANY, cleanup: bool = True):
        cookies = user.cookies

        list_in = BaseList(
            name = list_name if list_name is not None else user.username,
            privacy = privacy
        )

        create_response = requests.post(BASE_URL_LISTS, json=asdict(list_in), cookies=cookies)

        assert create_response.status_code == 200, create_response.json()
        assert create_response.json().keys() == SUCCESS_CREATING_MSG.keys()
        assert create_response.json()["message"] == SUCCESS_CREATING_MSG["message"]

        if cleanup:
            responses.append({"list_id": create_response.json()["list_id"], "cookies": cookies})

        list_in.list_id = create_response.json()["list_id"]

        return list_in

    yield _create_list

    # Limpa do DB depois
    for r in responses:
        list_id, cookies = r["list_id"], r["cookies"]
        del_response = requests.delete(BASE_URL_LISTS + f"/{list_id}", cookies=cookies)
        assert del_response.status_code == 200, del_response.json()
        assert del_response.json() == SUCCESS_DELETING_MSG


@pytest.fixture
def edit_list_request():
    """Faz o request para editar uma review de usuário."""

    # Tenta editar a lista no DB
    def _edit_list_request(user: BaseUser, list_in: BaseList):
        edit_resp = requests.put(f"{BASE_URL_LISTS}/{list_in.list_id}", cookies=user.cookies, json=asdict(list_in))
        return edit_resp

    return _edit_list_request


@pytest.fixture
def add_game_request():
    """Faz o request para adicionar um game à lista de um usuário.
    cleanup = True significa que vai remover o game da lista depois da função acabar"""

    responses = []

    def _add_game_request(user: BaseUser, list_in: BaseList, game_id: int, cleanup: bool = False):
        list_id = list_in.list_id
        add_resp = requests.post(f"{BASE_URL_LISTS}/game/{list_id}/{game_id}", cookies=user.cookies)

        if cleanup:
            assert add_resp.status_code == 200, add_resp.json()
            responses.append({"list_id": list_id, "game_id": game_id, "cookies": user.cookies})

        return add_resp

    yield _add_game_request

    for r in responses:
        list_id, game_id, cookies = r["list_id"], r["game_id"], r["cookies"]
        del_response = requests.delete(f"{BASE_URL_LISTS}/game/{list_id}/{game_id}", cookies=cookies)
        assert del_response.status_code == 200, del_response.json()
        assert del_response.json() == SUCCEESS_REMOVING_MSG


@pytest.fixture()
def rem_game_request():
    """Faz o request para remover um game à lista de um usuário"""

    # Tenta fazer um usuário remover um game da sua lista.
    def _rem_game_request(user: BaseUser, list_in: BaseList, game_id: int):
        list_id = list_in.list_id
        rem_resp = requests.delete(f"{BASE_URL_LISTS}/game/{list_id}/{game_id}", cookies=user.cookies)

        return rem_resp

    return _rem_game_request


@pytest.fixture
def save_list_request():
    """Faz o request para um usuário salvar uma lista.
    cleanup = True significa que vai remover o game da lista depois da função acabar"""

    responses = []

    # Tenta salvar a lista na biblioteca do usuário
    def _save_list_request(user: BaseUser, list_in: BaseList, cleanup: bool = False):
        save_response = requests.post(BASE_URL_LISTS + f"/save/{list_in.list_id}", cookies=user.cookies)

        if cleanup:
            assert save_response.status_code == 200, save_response.json()
            responses.append({"list_id": list_in.list_id, "cookies": user.cookies})

        return save_response

    yield _save_list_request

    # Limpa do DB
    for r in responses:
        unsave_response = requests.delete(BASE_URL_LISTS + f"/save/{r["list_id"]}", cookies=r["cookies"])
        assert unsave_response == 200, unsave_response.json()
        assert unsave_response.json() == SUCCEESS_UNSAVING_MSG


@pytest.fixture()
def unsave_list_request():
    """Faz o request para um usuário dessalvar uma lista"""

    def _unsave_list_request(user: BaseUser, list_in: BaseList):
        return requests.delete(
            BASE_URL_LISTS + f"/save/{list_in.list_id}",
            cookies=user.cookies
        )

    return _unsave_list_request


@pytest.fixture()
def get_list_request():
    """Faz o request para pegar os dados completos de uma lista no DB"""

    def _get_list_request(user: BaseUser, list_in: BaseList):
        return requests.get(
            BASE_URL_LISTS + f"/{list_in.list_id}",
            cookies = user.cookies
        )

    return _get_list_request