from dataclasses import asdict
import pytest
import requests

from ..utils import BaseUser, BaseList, Clearence, BASE_URL_LISTS, NOT_LOGGED_IN_MSG, LIST_NOT_FOUND_MSG, assert_block
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


def test_unsaving_your_own_list_returns_403(users, create_list, unsave_list_request):
    """Alice cria uma lista e tenta dessalvala""" 

    user1 = users("Alice")
    list_in = create_list(user1)

    unsave_response = unsave_list_request(user1, list_in)
    assert unsave_response.status_code == 403, unsave_response.json()
    assert unsave_response.json() == CANT_UNSAVE_CREATED_LIST


def test_changing_privacy_removes_saves(users, create_list, save_list_request, edit_list_request):
    """Alice cria uma lista publica, Bernado e Caua seguem a lista, Alice muda a lista para privada""" 

    user1, user2, user3 = users("Bernardo"), users("Caua"), users("Alice")
    list_in = create_list(user3)

    save_response = save_list_request(user1, list_in)
    assert save_response.status_code == 200, save_response.json()

    save_response = save_list_request(user2, list_in)
    assert save_response.status_code == 200, save_response.json()

    list_in.privacy = Clearence.OWNER    

    edit_response = edit_list_request(user3, asdict(list_in))
    assert edit_response.status_code == 200, edit_response.json()

    assert_unsave(user1, list_in)
    assert_unsave(user2, list_in)


def test_blocking_stops_saves(users, block_request, create_list, save_list_request):
    """Alice cria uma lista publica, Alice bloqueia Bernado, Bernardo tenta salvar a lista de Alice"""

    user1, user2 = users("Bernardo"), users("Alice")
    list_in = create_list(user2, privacy=Clearence.ANY)

    block_response = block_request(user2, user1, True)
    assert block_response.status_code == 200, block_response.json()
    assert_block(user2, user1)

    save_response = save_list_request(user1, list_in)
    assert save_response.status_code == 433, save_response.json()
    assert save_response.json() == BLOCKED_BY_LIST_OWNER_MSG
    assert_unsave(user1, list_in)


def test_blocking_removes_saves_between_both_users(users, create_list, save_list_request, block_request):
    """Alice cria uma lista publica, Bernardo salva a lista de Alice, Alice bloqueia Bernardo, a lista de Alice deve ser removida da biblioteca de Bernardo"""
    alice = users("Alice")
    bernardo = users("Bernardo")

    alice_list = create_list(alice, privacy=Clearence.ANY)
    bernardo_list = create_list(bernardo, privacy=Clearence.ANY)

    response = save_list_request(bernardo, alice_list)
    assert response.status_code == 200, response.json()

    response = save_list_request(alice, bernardo_list)
    assert response.status_code == 200, response.json()

    response = block_request(alice, bernardo)
    assert response.status_code == 200, response.json()

    assert_unsave(bernardo, alice_list)
    assert_unsave(alice, bernardo_list)
    

