from .utils import *


@pytest.fixture
def create_list():
    """Insere uma lista no DB
    se cleanup == True, vai remover do DB depois que a função teste rodar"""

    lists = []

    def _create_list(user: BaseUser, list_name: str = None, privacy: int = Clearence.ANY, cleanup: bool = True):
        """Cria uma lista para o usuário"""
        cookies = user.cookies

        list_in = BaseList(
            name = list_name if list_name is not None else user.username,
            privacy = privacy
        )

        create_response = requests.post(BASE_URL_LISTS, json=asdict(list_in), cookies=cookies)
        assert create_response.status_code == 200, create_response.json()
        list_id = create_response.json()["list_id"]
        list_in.list_id = list_id

        if cleanup:
            lists.append({"list_id": list_id, "cookies": cookies})

        return list_in

    def _cleanup():
        """Apaga todas as listas criadas até agora"""
        while len(lists) > 0:
            l = lists.pop()
            list_id, cookies = l["list_id"], l["cookies"]
            del_response = requests.delete(BASE_URL_LISTS + f"/{list_id}", cookies=cookies)
            assert del_response.status_code == 200, del_response.json()


    _create_list.cleanup = _cleanup

    yield _create_list

    _cleanup()


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

    games = []

    def _add_game_request(user: BaseUser, list_in: BaseList, game_id: int, cleanup: bool = False):
        """Tenta adicionar um game à lista do usuário"""

        list_id = list_in.list_id
        add_resp = requests.post(f"{BASE_URL_LISTS}/game/{list_id}/{game_id}", cookies=user.cookies)

        if cleanup:
            assert add_resp.status_code == 200, add_resp.json()
            games.append({"list_id": list_id, "game_id": game_id, "cookies": user.cookies})

        return add_resp

    def _cleanup():
        """Apaga todos os games da lista de um usuário que foram adicionados até aqui"""

        while len(games) > 0:
            g = games.pop()
            list_id, game_id, cookies = g["list_id"], g["game_id"], g["cookies"]
            del_response = requests.delete(f"{BASE_URL_LISTS}/game/{list_id}/{game_id}", cookies=cookies)
            assert del_response.status_code == 200, del_response.json()

    _add_game_request.cleanup = _cleanup

    yield _add_game_request

    _cleanup()


@pytest.fixture()
def rem_game_request():
    """Faz o request para remover um game à lista de um usuário"""

    def _rem_game_request(user: BaseUser, list_in: BaseList, game_id: int):
        """Tenta remover um game da lista do usuário"""
        list_id = list_in.list_id
        rem_resp = requests.delete(f"{BASE_URL_LISTS}/game/{list_id}/{game_id}", cookies=user.cookies)

        return rem_resp

    return _rem_game_request


@pytest.fixture
def save_list_request():
    """Faz o request para um usuário salvar uma lista.
    cleanup = True significa que vai remover o game da lista depois da função acabar"""

    lists = []

    def _save_list_request(user: BaseUser, list_in: BaseList, cleanup: bool = False):
        """Tenta salvar uma lista na biblioteca do usuário"""

        save_response = requests.post(BASE_URL_LISTS + f"/save/{list_in.list_id}", cookies=user.cookies)
        if cleanup:
            assert save_response.status_code == 200, save_response.json()
            lists.append({"list_id": list_in.list_id, "cookies": user.cookies})

        return save_response

    def _cleanup():
        """Remove da biblioteca do usuário as listas salvas até agora"""

        while len(lists) > 0:
            l = lists.pop()
            unsave_response = requests.delete(BASE_URL_LISTS + f"/save/{l["list_id"]}", cookies=l["cookies"])
            assert unsave_response == 200, unsave_response.json()

    _save_list_request.cleanup = _cleanup

    yield _save_list_request

    _cleanup()


@pytest.fixture()
def unsave_list_request():
    """Faz o request para um usuário dessalvar uma lista"""

    def _unsave_list_request(user: BaseUser, list_in: BaseList):
        """Tenta remover uma lista da biblioteca do usuário"""

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


@pytest.fixture()
def delete_list_request():
    """Faz o request para deletar uma lista do DB"""

    def _delete_list_request(user: BaseUser, list_in: BaseList):
        return requests.delete(
            BASE_URL_LISTS + f"/{list_in.list_id}",
            cookies = user.cookies
        )

    return _delete_list_request