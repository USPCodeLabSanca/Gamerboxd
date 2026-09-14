from . import *
from .utils import *

def save_list_request(atv: dict, pas: dict, list_in: dict):
    return requests.post(
        url=BASE_URL + f"/save/{pas["username"]}/{list_in["name"]}",
        cookies=atv["cookies"]
    )


def unsave_list_request(atv: dict, pas: dict, list_in: dict):
    return requests.delete(
        url=BASE_URL + f"/save/{pas["username"]}/{list_in["name"]}",
        cookies=atv["cookies"]
    )


def view_list_saves(user: dict):
    response = requests.get(url= BASE_URL + f"/saved", cookies=user["cookies"])
    assert response.status_code == 200
    return response.json()["lists"]


def assert_save(atv: dict, pas: dict, list_in: dict):
    lists = view_list_saves(atv)
    assert any([pas["username"] == l["creator"] and list_in["name"] == l["name"] for l in lists])


def assert_unsave(atv: dict, pas: dict, list_in: dict):
    lists = view_list_saves(atv)
    assert all([pas["username"] != l["creator"] and list_in["name"] != l["name"] for l in lists])


# ========= Testes ===========

def test_creating_automatically_saves(users):
    """Alice cria uma lista, isso deve automaticamente salvar a lista de Alice"""

    user = users["Alice"]
    list_in = create_list(user)
    assert_save(user, user, list_in)
    delete_list(user, list_in)


def test_saving_and_unsaving_list(users):
    """Alice cria uma lista publica, Bernardo salva e depois dessalva a lista de Alice"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2)

    save_response = save_list_request(user1, user2, list_in)
    assert save_response.status_code == 200
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(user1, user2, list_in)

    unsave_response = unsave_list_request(user1, user2, list_in)
    assert unsave_response.status_code == 200
    assert unsave_response.json() == SUCCEESS_UNSAVING_MSG
    assert_unsave(user1, user2, list_in)

    delete_list(user2, list_in)


def test_saving_private_list(users):
    """Alice cria uma lista privada, Bernardo tentar salvar a lista de Alice"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2, privacy=True)

    save_response = save_list_request(user1, user2, list_in)
    assert save_response.status_code == 404
    assert save_response.json() == LIST_NOT_FOUND_MSG
    assert_unsave(user1, user2, list_in)

    delete_list(user2, list_in)


def test_saving_non_existent_list(users):
    """Alice tenta salvar e desalvar uma lista que não existe"""

    user1, user2 = users["Alice"], users["Bernardo"]
    list_in = {"name": "ghost"}

    save_response = save_list_request(user1, user2, list_in)
    assert save_response.status_code == 404
    assert save_response.json() == LIST_NOT_FOUND_MSG

    unsave_response = unsave_list_request(user1, user2, list_in)
    assert unsave_response.status_code == 404
    assert unsave_response.json() == LIST_NOT_FOUND_MSG


def test_saving_list_from_non_existent_user(users):
    """Alice tenta salvar e dessalvar a lista de um usuario que não existe"""

    user1, inexistent = users["Alice"], {"username": "ghost"}
    list_in = {"name": "ghost"}

    save_response = save_list_request(user1, inexistent, list_in)
    assert save_response.status_code == 404
    assert save_response.json() == USER_NOT_FOUND_MSG

    unsave_response = unsave_list_request(user1, inexistent, list_in)
    assert unsave_response.status_code == 404
    assert unsave_response.json() == USER_NOT_FOUND_MSG


def test_deleting_list_cascades(users):
    """Alice cria uma lista, Bernardo segue a lista, Alice deleta a lista"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2)

    save_response = save_list_request(user1, user2, list_in)
    assert save_response.status_code == 200
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(user1, user2, list_in)

    delete_list(user2, list_in)
    assert_unsave(user1, user2, list_in)


def test_unsaving_your_own_list(users):
    """Alice cria uma lista e tenta dessalvala""" 

    user1, user2 = users["Alice"], users["Alice"]
    list_in = create_list(user2)

    unsave_response = unsave_list_request(user1, user2, list_in)
    assert unsave_response.status_code == 403
    assert unsave_response.json() == {"message": "Não é possível dessalvar sua própria lista, apenas deletá-la!"}
    delete_list(user2, list_in)


def test_changing_privacy_removes_saves(users):
    """Alice cria uma lista publica, Bernado e Caua seguem a lista, Alice muda a lista para privada""" 

    user1, user2, user3 = users["Bernardo"], users["Caua"], users["Alice"]
    list_in = create_list(user3)

    save_response = save_list_request(user1, user3, list_in)
    assert save_response.status_code == 200
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(user1, user3, list_in)

    save_response = save_list_request(user2, user3, list_in)
    assert save_response.status_code == 200
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(user1, user3, list_in)

    set_privacy(user3, list_in, True)
    assert_unsave(user1, user3, list_in)
    assert_unsave(user2, user3, list_in)

    delete_list(user3, list_in)


def test_blocking_stops_saves(users):
    """Alice cria uma lista publica, Alice bloqueia Bernado , Bernardo tenta salvar a lista de Alice"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2)

    block_response = block(user2, user1)
    assert block_response.status_code == 200
    assert_block(user2, user1)

    save_response = save_list_request(user1, user2, list_in)
    assert save_response.status_code == 403
    assert save_response.json() == {"message": "Usuário está tentando salvar lista de alguém que o bloqueou"}
    assert_unsave(user1, user2, list_in)

    delete_list(user2, list_in)









    

