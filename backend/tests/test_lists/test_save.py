import pytest
import requests

from ..utils import BaseUser, BaseList, Clearence, BASE_URL_LISTS, NOT_LOGGED_IN_MSG, LIST_NOT_FOUND_MSG
from .utils import PRIVATE_LIST_MSG, BLOCKED_BY_LIST_OWNER_MSG, assert_save, assert_unsave

SUCCESS_SAVING_MSG = {"message": "Lista salva com sucesso!"}
SUCCEESS_UNSAVING_MSG = {"message": "Lista dessalva com sucesso!"}
CANT_UNSAVE_CREATED_LIST = {"message": "O usuário está tentando dessalvar sua própria lista!"}


def test_creating_automatically_saves(users, create_list):
    """Alice cria uma lista, o que salva automaticamente a lista de Alice"""

    user = users("Alice")
    list_in = create_list(user)
    assert_save(user, list_in)


def test_saving_list_returns_200(users, create_list, save_list_request):
    """Alice cria uma lista publica, Bernardo salva a lista de Alice"""

    saver, creator = users("Bernardo"), users("Alice")
    list_in = create_list(creator)

    save_response = save_list_request(saver, list_in)
    assert save_response.status_code == 200, save_response.json()
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(saver, list_in)


def test_unsaving_list_returns_200(users, create_list, save_list_request, unsave_list_request):
    """Alice cria uma lista publica, Bernardo salva e depois dessalva a lista de Alice"""

    saver, creator = users("Bernardo"), users("Alice")
    list_in = create_list(creator)

    save_response = save_list_request(saver, list_in)
    assert save_response.status_code == 200, save_response.json()
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(saver, list_in)

    unsave_response = unsave_list_request(saver, list_in)
    assert unsave_response.status_code == 200, unsave_response.json()
    assert unsave_response.json() == SUCCEESS_UNSAVING_MSG
    assert_unsave(saver, list_in)


@pytest.mark.parametrize("privacy", [Clearence.FOLLOWED, Clearence.OWNER])
def test_saving_private_list_returns_403(users, privacy, create_list, save_list_request):
    """Alice cria uma lista privada, Bernardo tenta salvar a lista de Alice"""

    saver, creator = users("Bernardo"), users("Alice")
    list_in = create_list(creator, privacy=privacy)

    save_response = save_list_request(saver, list_in)
    assert save_response.status_code == 403, save_response.json()
    assert save_response.json() == PRIVATE_LIST_MSG
    assert_unsave(saver, list_in)

    
def test_saving_list_twice_returns_200_twice(users, create_list, save_list_request):
    """Alice cria uma lista publica, Bernardo salva a lista de Alice"""

    saver, creator = users("Bernardo"), users("Alice")
    list_in = create_list(creator)

    save_response = save_list_request(saver, list_in)
    assert save_response.status_code == 200, save_response.json()

    save_response = save_list_request(saver, list_in)
    assert save_response.status_code == 200, save_response.json()


def test_saving_non_existent_list_returns_404(users, save_list_request, unsave_list_request):
    """Alice tenta salvar uma lista que não existe"""

    user = users("Alice")
    list_in = BaseList(list_id = "inexistent")

    save_response = save_list_request(user, list_in)
    assert save_response.status_code == 404, save_response.json()
    assert save_response.json() == LIST_NOT_FOUND_MSG


def test_unsaving_non_existent_list_returns_404(users, unsave_list_request):
    """Alice tenta desalvar uma lista que não existe"""

    user = users("Alice")
    list_in = BaseList(list_id = "inexistent")

    unsave_response = unsave_list_request(user, list_in)
    assert unsave_response.status_code == 404, unsave_response.json()
    assert unsave_response.json() == LIST_NOT_FOUND_MSG


def test_unsaving_your_own_list_returns_403(users, create_list, unsave_list_request):
    """Alice cria uma lista e tenta dessalvala""" 

    creator = users("Alice")
    list_in = create_list(creator)

    unsave_response = unsave_list_request(creator, list_in)
    assert unsave_response.status_code == 403, unsave_response.json()
    assert unsave_response.json() == CANT_UNSAVE_CREATED_LIST
    assert_save(creator, list_in)


def test_blocking_stops_saves(users, block_request, create_list, save_list_request):
    """Alice cria uma lista publica, Alice bloqueia Bernado, Bernardo tenta salvar a lista de Alice"""

    saver, creator = users("Bernardo"), users("Alice")
    list_in = create_list(creator, privacy=Clearence.ANY)

    block_response = block_request(creator, saver, True)
    assert block_response.status_code == 200, block_response.json()

    save_response = save_list_request(saver, list_in)
    assert save_response.status_code == 433, save_response.json()
    assert save_response.json() == BLOCKED_BY_LIST_OWNER_MSG
    assert_unsave(saver, list_in)


def test_saving_list_while_not_logged_in_returns_401():
    """Um usuário tenta salvar uma lista sem enviar os cookies"""

    response = requests.post(url=BASE_URL_LISTS + "/save/abc")
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG


def test_unsaving_list_while_not_logged_in_returns_401():
    """Um usuário tenta dessalvar uma lista sem enviar os cookies"""

    response = requests.delete(url=BASE_URL_LISTS + "/save/abc")
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG


def test_list_saving_pagination(pagination_tests, users, create_list, save_list_request):
    """Alice salva várias listas de Bernardo"""

    def seed(saver: BaseUser, total: int, order: str = "", search: str = None):
        """Cria várias listas e faz o saver salvar elas"""

        list_names = [f"List{i+1}" for i in range(total-2)] if search is None else [(search + "_" * i) for i in range(total)]
        new_lists = [create_list(users("Bernardo"), list_name = l) for l in list_names]

        for nl in new_lists:
            response = save_list_request(saver, nl)
            assert response.status_code == 200, response.json()
            
        if ("!" in order) or (len(order) == 0):
            list_names.reverse()

        return list_names

    seed.cleanup = create_list.cleanup
    seed.expected_content = ["list_id", "name", "creator", "saves_count", "cover_picture", "rel", "privacy"]
    seed.valid_orders = ["created_at", "name"]
    seed.searches = ["Playstation", "Minecraft", "Esporte"]
    seed.return_obj = "name"
    seed.ignore = ["Jogos Completados", "Jogos Favoritos"]
    
    pagination_tests(
        user = users("Alice"),
        url = BASE_URL_LISTS + f"/save",
        seed = seed,
        require_login = False
    )
    

