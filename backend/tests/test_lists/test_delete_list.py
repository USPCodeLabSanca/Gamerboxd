from .utils import *


def test_deleting_list_returns_200(users, create_list, delete_list_request, get_list_request):
    """Alice cria e deleta uma lista"""

    creator = users["Alice"]
    list_in = create_list(creator, cleanup=False)

    delete_response = delete_list_request(creator, list_in)
    assert delete_response.status_code == 200, delete_response.json()
    assert delete_response.json() == SUCCESS_DELETING_MSG

    get_response = get_list_request(creator, list_in)
    assert get_response.status_code == 404, get_response.json()
    assert get_response.json() == LIST_NOT_FOUND_MSG


def test_deleting_twice_returns_404(users, create_list, delete_list_request):
    """Alice cria e deleta uma lista e tenta deletar uma segunda vez"""

    creator = users["Alice"]
    list_in = create_list(creator, cleanup=False)

    delete_response = delete_list_request(creator, list_in)
    assert delete_response.status_code == 200, delete_response.json()

    delete_response = delete_list_request(creator, list_in)
    assert delete_response.status_code == 404, delete_response.json()
    assert delete_response.json() == LIST_NOT_FOUND_MSG


def test_deleting_list_you_dont_own_returns_403(users, create_list, delete_list_request):
    """Alice cria uma lista, Bernardo tenta deletar a lista de Alice"""

    creator, deleter = users["Alice"], users["Bernardo"]
    list_in = create_list(creator)   
    
    delete_response = delete_list_request(deleter, list_in)
    assert delete_response.status_code == 403, delete_response.json()
    assert delete_response.json() == LACK_OF_LIST_OWNERSHIP_MSG


def test_deleting_list_cascades_to_saved_lists(users, create_list, save_list_request, delete_list_request):
    """Alice cria uma lista, Bernardo salva a lista, Alice deleta a lista"""

    creator, saver = users["Alice"], users["Bernardo"]
    list_in = create_list(creator, cleanup=False)

    save_response = save_list_request(saver, list_in)
    assert save_response.status_code == 200, save_response.json()

    delete_response = delete_list_request(creator, list_in)
    assert delete_response.status_code == 200, delete_response.json()
    assert_unsave(saver, list_in)