import copy
from dataclasses import asdict
import pytest
import requests

from ..utils import BASE_URL_USERS, NOT_LOGGED_IN_MSG
from .utils import USERNAME_IN_USE_MSG, USERNAME_WRONG_LENGTH_MSG, EMAIL_IN_USE_MSG, INVALID_EMAIL_MSG

BIO_WRONG_LENGTH_MSG = {"message": "A bio não pode ter mais que 280 caracteres!"}
BIO_EMPTY_MSG = {"message": "A bio não pode ser apenas espaço vazio!"}

@pytest.mark.parametrize("field, new_value, expected_status, expected_body", [
    pytest.param("username", "Alice", 200, None, id="Mesmo username de antes"),
    pytest.param("username", "Lucas", 200, None, id="Novo username ok"),
    pytest.param("username", "Joao ", 200, None, id="Username com trailing space"),
    pytest.param("username", "Alex", 200, None, id="Username no limite inferior de caracteres"),
    pytest.param("username", "Ali"*8, 200, None, id="Username no limite superior de caracteres"),
    pytest.param("username", "Joana", 409, USERNAME_IN_USE_MSG("Joana"), id="Username já em uso"),
    pytest.param("username", "Ali"*9, 400, USERNAME_WRONG_LENGTH_MSG, id="Username muito longo"),
    pytest.param("username", "A", 400, USERNAME_WRONG_LENGTH_MSG, id="Username muito curto"),
    pytest.param("username", 4222, 422, None, id="Username como um int"),
    pytest.param("username", None, 422, None, id="Username como null"),
    pytest.param("bio", "Curto ação e corrida!", 200, None, id="Bio ok"),
    pytest.param("bio", "Curto ação!          ", 200, None, id="Bio com trailing spaces"),
    pytest.param("bio", "Games"*56, 200, None, id="Bio no limite dos caractéres"),
    pytest.param("bio", None, 200, None, id="Bio como null"),
    pytest.param("bio", "Alice"*61, 400, BIO_WRONG_LENGTH_MSG, id="Bio muito longa"),
    pytest.param("bio", "        ", 400, BIO_EMPTY_MSG, id="Bio apenas espaço vazio"),
    pytest.param("bio", 4220, 422, None, id="Bio como int"),
    pytest.param("pfp", "frontend/images/ok", 200, None, id="Pfp com path válido"),
    pytest.param("pfp", None, 200, None, id="Pfp como null"),
    pytest.param("pfp", 4220, 422, None, id="Pfp como int"),
    pytest.param("banner", "frontend/images/ok", 200, None, id="Banner com path válido"),
    pytest.param("banner", None, 200, None, id="Banner como null"),
    pytest.param("banner", 4220, 422, None, id="Banner como int"),
])
def test_editing_user_account_checks_edge_cases(users, edit_user_request, field, new_value, expected_status, expected_body):
    """Alice troca o seu detalhes da sua conta"""

    user = users("Alice")
    edited_user = asdict(copy.copy(user))
    edited_user[field] = new_value

    if expected_status == 409:
        users(new_value[:new_value.find("@")]) if "@" in new_value else users(new_value)

    reset = user if expected_status == 200 else None
    response = edit_user_request(edited_user, reset)
    assert response.status_code == expected_status, response.json()

    if expected_status == 200: 
        if type(new_value) == str:
            assert response.json()[field].strip() == edited_user[field].strip()

        else:
            assert response.json()[field] == edited_user[field]

    elif expected_body is not None:
        assert response.json() == expected_body


@pytest.mark.parametrize("field_to_remove", ["username", "bio", "email", "pfp", "banner"])
def test_not_sending_all_fields_returns_422(users, edit_user_request, field_to_remove):
    """Alice tenta editar sua conta, mas não envia todos os campos necessários"""

    user = users("Alice")
    user_edit = asdict(copy.copy(user))
    user_edit.pop(field_to_remove)

    response = edit_user_request(user_edit)
    assert response.status_code == 422, response.json()


def test_editing_account_while_not_logged_in_returns_401():
    """Um usuário tenta editar sua_conta sem enviar os seus cookies de autenticação"""

    response = requests.put(BASE_URL_USERS, json={"username": "Alice"})
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG