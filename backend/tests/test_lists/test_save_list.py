from .utils import *


def test_creating_automatically_saves(users, create_list):
    """Alice cria uma lista, isso deve automaticamente salvar a lista de Alice"""

    user = users["Alice"]
    list_in = create_list(user)
    assert_save(user, list_in)


def test_saving_and_unsaving_list_returns_200(users, create_list, save_list_request, unsave_list_request):
    """Alice cria uma lista publica, Bernardo salva e depois dessalva a lista de Alice"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2)

    save_response = save_list_request(user1, list_in)
    assert save_response.status_code == 200, save_response.json()
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(user1, list_in)

    unsave_response = unsave_list_request(user1, list_in)
    assert unsave_response.status_code == 200, unsave_response.json()
    assert unsave_response.json() == SUCCEESS_UNSAVING_MSG
    assert_unsave(user1, list_in)


def test_saving_private_list_returns_403(users, create_list, save_list_request):
    """Alice cria uma lista privada, Bernardo tentar salvar a lista de Alice"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2, privacy=True)

    save_response = save_list_request(user1, list_in)
    assert save_response.status_code == 403, save_response.json()
    assert save_response.json() == PRIVATE_LIST_MSG
    assert_unsave(user1, list_in)


def test_saving_non_existent_list_returns_404(users, save_list_request, unsave_list_request):
    """Alice tenta salvar e desalvar uma lista que não existe"""

    user = users["Alice"]
    list_in = BaseList(list_id = "inexistent")

    save_response = save_list_request(user, list_in)
    assert save_response.status_code == 404, save_response.json()
    assert save_response.json() == LIST_NOT_FOUND_MSG

    unsave_response = unsave_list_request(user, list_in)
    assert unsave_response.status_code == 404, unsave_response.json()
    assert unsave_response.json() == LIST_NOT_FOUND_MSG


def test_deleting_list_cascades_to_saved_lists(users, create_list, save_list_request):
    """Alice cria uma lista, Bernardo salva a lista, Alice deleta a lista"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2, cleanup=False)

    save_response = save_list_request(user1, list_in)
    assert save_response.status_code == 200, save_response.json()

    delete_response = requests.delete(BASE_URL_LISTS + f"/{list_in.list_id}", cookies=user2.cookies)
    assert delete_response.status_code == 200, delete_response.json()
    assert_unsave(user1, list_in)


def test_unsaving_your_own_list_returns_403(users, create_list, unsave_list_request):
    """Alice cria uma lista e tenta dessalvala""" 

    user1 = users["Alice"]
    list_in = create_list(user1)

    unsave_response = unsave_list_request(user1, list_in)
    assert unsave_response.status_code == 403, unsave_response.json()
    assert unsave_response.json() == CANT_UNSVAE_CREATED_LIST


def test_changing_privacy_removes_saves(users, create_list, save_list_request, edit_list_request):
    """Alice cria uma lista publica, Bernado e Caua seguem a lista, Alice muda a lista para privada""" 

    user1, user2, user3 = users["Bernardo"], users["Caua"], users["Alice"]
    list_in = create_list(user3)

    save_response = save_list_request(user1, list_in)
    assert save_response.status_code == 200, save_response.json()

    save_response = save_list_request(user2, list_in)
    assert save_response.status_code == 200, save_response.json()

    list_in.privacy = Clearence.OWNER    

    edit_response = edit_list_request(user3, list_in)
    assert edit_response.status_code == 200, edit_response.json()

    assert_unsave(user1, list_in)
    assert_unsave(user2, list_in)


def test_blocking_stops_saves(users, block_request, create_list, save_list_request):
    """Alice cria uma lista publica, Alice bloqueia Bernado, Bernardo tenta salvar a lista de Alice"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2, privacy=Clearence.ANY)

    block_response = block_request(user2, user1, True)
    assert block_response.status_code == 200, block_response.json()
    assert_block(user2, user1)

    save_response = save_list_request(user1, list_in)
    assert save_response.status_code == 403, save_response.json()
    assert save_response.json() == BLOCKED_BY_LIST_OWNER_MSG
    assert_unsave(user1, list_in)
    

