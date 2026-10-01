from .utils import *

def save_list(user: dict, list_in: dict):
    return requests.post(
        url=BASE_URL + f"/save/{list_in["list_id"]}",
        cookies=user["cookies"]
    )


def unsave_list(user: dict, list_in: dict):
    return requests.delete(
        url=BASE_URL + f"/save/{list_in["list_id"]}",
        cookies=user["cookies"]
    )


def view_list_saves(user: dict):
    """Retorna as listas salvas por um usuário"""

    cookies = user["cookies"]
    saved_lists = []

    response = requests.get(f"{BASE_URL}/saved", cookies=cookies)
    assert response.status_code == 200
    response_json = response.json()
    saved_lists += response_json["content"]

    while response_json["next_page"] != None:
        response = requests.get(response_json["next_page"], cookies=cookies)
        assert response.status_code == 200
        response_json = response.json()
        saved_lists += response_json["content"]

    return saved_lists


def assert_save(user: dict, list_in: dict):
    saved_lists = view_list_saves(user)
    assert any([list_in["list_id"] == sl["list_id"] for sl in saved_lists])


def assert_unsave(user: dict, list_in: dict):
    saved_lists = view_list_saves(user)
    assert all([list_in["list_id"] != sl["list_id"] for sl in saved_lists])


# ========= Testes ===========

def test_creating_automatically_saves(users):
    """Alice cria uma lista, isso deve automaticamente salvar a lista de Alice"""

    user = users["Alice"]
    list_in = create_list(user)
    assert_save(user, list_in)
    delete_list(user, list_in)


def test_saving_and_unsaving_list_returns_200(users):
    """Alice cria uma lista publica, Bernardo salva e depois dessalva a lista de Alice"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2)

    save_response = save_list(user1, list_in)
    assert save_response.status_code == 200
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(user1, list_in)

    unsave_response = unsave_list(user1, list_in)
    assert unsave_response.status_code == 200
    assert unsave_response.json() == SUCCEESS_UNSAVING_MSG
    assert_unsave(user1, list_in)

    delete_list(user2, list_in)


def test_saving_private_list_returns_403(users):
    """Alice cria uma lista privada, Bernardo tentar salvar a lista de Alice"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2, privacy=True)

    save_response = save_list(user1, list_in)
    assert save_response.status_code == 403
    assert save_response.json() == PRIVATE_LIST_MSG
    assert_unsave(user1, list_in)

    delete_list(user2, list_in)


def test_saving_non_existent_list_returns_404(users):
    """Alice tenta salvar e desalvar uma lista que não existe"""

    user = users["Alice"]
    list_in = {"list_id": "ghost"}

    save_response = save_list(user, list_in)
    assert save_response.status_code == 404
    assert save_response.json() == LIST_NOT_FOUND_MSG

    unsave_response = unsave_list(user, list_in)
    assert unsave_response.status_code == 404
    assert unsave_response.json() == LIST_NOT_FOUND_MSG


def test_deleting_list_cascades_to_saved_lists(users):
    """Alice cria uma lista, Bernardo sALVA a lista, Alice deleta a lista"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2)

    save_response = save_list(user1, list_in)
    assert save_response.status_code == 200
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(user1, list_in)

    delete_list(user2, list_in)
    assert_unsave(user1, list_in)


def test_unsaving_your_own_list_returns_403(users):
    """Alice cria uma lista e tenta dessalvala""" 

    user1 = users["Alice"]
    list_in = create_list(user1)

    unsave_response = unsave_list(user1, list_in)
    assert unsave_response.status_code == 403
    assert unsave_response.json() == {"message": "Não é possível dessalvar sua própria lista, apenas deletá-la!"}
    delete_list(user1, list_in)


def test_changing_privacy_removes_saves(users):
    """Alice cria uma lista publica, Bernado e Caua seguem a lista, Alice muda a lista para privada""" 

    user1, user2, user3 = users["Bernardo"], users["Caua"], users["Alice"]
    list_in = create_list(user3)

    save_response = save_list(user1, list_in)
    assert save_response.status_code == 200
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(user1,list_in)

    save_response = save_list(user2, list_in)
    assert save_response.status_code == 200
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(user1, list_in)

    set_privacy(user3, list_in, True)
    assert_unsave(user1, list_in)
    assert_unsave(user2, list_in)

    delete_list(user3, list_in)


def test_blocking_stops_saves(users, block):
    """Alice cria uma lista publica, Alice bloqueia Bernado, Bernardo tenta salvar a lista de Alice"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2)

    block_response = block(user2, user1, True)
    assert block_response.status_code == 200
    assert_block(user2, user1)

    save_response = save_list(user1, list_in)
    assert save_response.status_code == 403
    assert save_response.json() == BLOCKED_BY_LIST_OWNER
    assert_unsave(user1, list_in)

    delete_list(user2, list_in)









    

