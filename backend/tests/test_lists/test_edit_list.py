from dataclasses import asdict
import pytest
import requests

from ..utils import Clearence, BASE_URL_LISTS, NOT_LOGGED_IN_MSG, LIST_NOT_FOUND_MSG
from .utils import (
    LIST_NAME_TAKEN_MSG, LIST_NAME_TOO_BIG_MSG, LIST_NAME_BLANK_MSG, 
    LIST_DESC_TOO_BIG_MSG, LIST_DESC_BLANK_MSG,
    LIST_PRIVACY_INVALID_MSG,
    LACK_OF_LIST_OWNERSHIP_MSG,
    assert_game_in_list, assert_game_not_in_list, assert_privacy
)

@pytest.mark.parametrize("field, new_value, expected_status, expected_body", [
    pytest.param("name", "Alice", 200, None, id="Same name as before"),
    pytest.param("name", "Lista", 200, None, id="Ok new name"),
    pytest.param("name", "List👍", 200, None, id="New name with emoji"),
    pytest.param("name", "List ", 200, None, id="Name with trailing space"),
    pytest.param("name", "Ali"*15, 200, None, id="Name at character limit"),
    pytest.param("name", "     ", 400, LIST_NAME_BLANK_MSG, id="Name completely blank"),
    pytest.param("name", "Ali"*16, 400, LIST_NAME_TOO_BIG_MSG, id="Name above character limit"),
    pytest.param("name", "Repetido", 409, LIST_NAME_TAKEN_MSG("Repetido"), id="Name already in use"),
    pytest.param("name", 4220, 422, None, id="Name as int"),
    pytest.param("name", None, 422, None, id="Name as null"),
    pytest.param("privacy", Clearence.ANY, 200, None, id="privacy at min"),
    pytest.param("privacy", Clearence.FOLLOWED, 200, None, id="privacy at med"),
    pytest.param("privacy", Clearence.OWNER, 200, None, id="privacy at max"),
    pytest.param("privacy", 21, 422, LIST_PRIVACY_INVALID_MSG, id="privacy invalid"),
    pytest.param("privacy", "secret", 422, None, id="privacy as str"),
    pytest.param("privacy", None, 422, None, id="privacy as null"),
    pytest.param("description", "Wishlist", 200, None, id="Ok new description"),
    pytest.param("description", "WishList👍", 200, None, id="New description with emoji"),
    pytest.param("description", "Wishlist ", 200, None, id="Description with trailing space"),
    pytest.param("description", "List"*75, 200, None, id="Description at character limit"),
    pytest.param("description", None, 200, None, id="Description as null"),
    pytest.param("description", "     ", 400, LIST_DESC_BLANK_MSG, id="Description completely blank"),
    pytest.param("description", "List"*76, 400, LIST_DESC_TOO_BIG_MSG, id="Description above character limit"),
    pytest.param("description", 4220, 422, None, id="Description as int"),
])
def test_editing_list_checks_edge_cases(users, create_list, edit_list_request, field, new_value, expected_status, expected_body):
    """Alice cria uma lista e troca o seu nome para um nome não utilizado"""

    creator = users("Alice")
    list_edit = asdict(create_list(creator))
    list_edit[field] = new_value

    if expected_status == 409:
        create_list(creator, list_name=new_value)
    
    edit_response = edit_list_request(creator, list_edit)
    assert edit_response.status_code == expected_status, edit_response.json()

    if expected_status == 200:
        if type(new_value) == str:
            assert edit_response.json()[field].strip() == list_edit[field].strip()

        else:
            assert edit_response.json()[field] == list_edit[field]

    elif expected_body is not None:
        assert edit_response.json() == expected_body



@pytest.mark.parametrize("field_to_remove", ["name", "privacy", "description"])
def test_not_sending_all_fields_when_editing_lists_returns_422(users, create_list, edit_list_request, field_to_remove):
    """Alice tenta editar sua lista, mas não envia todos os campos necessários"""

    editor = users("Alice")
    list_edit = asdict(create_list(editor))
    list_edit.pop(field_to_remove)

    response = edit_list_request(editor, list_edit)
    assert response.status_code == 422, response.json()


def test_edit_list_not_found_returns_404(users, create_list, edit_list_request):
    """Alice tenta editar uma lista que não existe"""

    editor = users("Alice")
    list_edit = create_list(editor)
    list_edit.list_id = "abc"

    edit_response = edit_list_request(editor, asdict(list_edit))
    assert edit_response.status_code == 404, edit_response.json()
    assert edit_response.json() == LIST_NOT_FOUND_MSG


def test_editing_list_while_not_logged_in_returns_401():
    """Um usuário tenta editar uma lista sem enviar os seus cookies de autenticação"""

    response = requests.put(BASE_URL_LISTS + "/abc", json={"privacy":Clearence.FOLLOWED})
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG


def test_someone_elses_list_returns_403(users, create_list, edit_list_request):
    """Alice cria uma lista, Bernardo tenta editar a lista de Alice"""

    creator, editor = users("Alice"), users("Bernardo")
    list_edit = create_list(creator)
    list_edit.privacy = Clearence.FOLLOWED

    edit_response = edit_list_request(editor, asdict(list_edit))
    assert edit_response.status_code == 403, edit_response.json()
    assert edit_response.json() == LACK_OF_LIST_OWNERSHIP_MSG

