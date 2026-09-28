from .utils import *

# users é um fixture definido em tests/conftest.py
# edit_user é um fixture definido em tests/test_users/conftest.py

def test_editing_username_to_unused_returns_200(users, edit_user):
    """Alice troca o seu username para Joao"""

    user = users["Alice"]
    edited_user = user.copy()
    edited_user["username"] = "Joao"

    response = edit_user(edited_user, user)
    assert response.status_code == 200, response.json()
    assert response.json()["username"] == edited_user["username"]


def test_editing_username_to_too_short_returns_400(users, edit_user):
    """Alice troca o seu username para um valor muito longo"""

    edited_user = users["Alice"].copy()
    edited_user["username"] = "Ali"

    response = edit_user(edited_user)
    assert response.status_code == 400,  response.json()
    assert response.json() == USERNAME_WRONG_LENGTH_MSG


def test_editing_username_to_too_long_returns_400(users, edit_user):
    """Alice troca o seu username para um valor muito longo"""

    edited_user = users["Alice"].copy()
    edited_user["username"] = "Alice" * 10 + "."

    response = edit_user(edited_user)
    assert response.status_code == 400, response.json()
    assert response.json() == USERNAME_WRONG_LENGTH_MSG


def test_editing_email_to_unused_returns_200(users, edit_user):
    """Alice troca o seu email para Joao@gmail.com"""

    user = users["Alice"]
    edited_user = user.copy()

    edited_user["email"] = "Joao@gmail.com"

    response = edit_user(edited_user, user)
    assert response.status_code == 200,  response.json()
    assert response.json()["email"] == edited_user["email"]


def test_editing_email_to_invalid_returns_400(users, edit_user):
    """Alice troca o seu email para Joao@gmail.com"""

    edited_user = users["Alice"].copy()
    edited_user["email"] = edited_user["username"]

    response = edit_user(edited_user)
    assert response.status_code == 400,  response.json()
    assert response.json() == {"message": "Email inválido!"}


def test_editing_user_info_to_unused_values_returns_200(users, edit_user):
    """Alice troca o seu username para Joao e seu email para Joao@gmail.com"""

    user = users["Alice"]
    edited_user = user.copy()

    edited_user["username"] = "Joao"
    edited_user["email"] = "Joao@gmail.com"

    response = edit_user(edited_user, user)
    assert response.status_code == 200, response.json()
    assert response.json()["username"] == edited_user["username"]
    assert response.json()["email"] == edited_user["email"]


def test_editing_username_to_used_value_returns_409(users, edit_user):
    """Alice troca seu username para Bernardo"""

    user_edit = users["Alice"].copy()
    user_already_exists = users["Bernardo"]

    user_edit["username"] = user_already_exists["username"]

    response = edit_user(user_edit)
    assert response.status_code == 409, response.json()
    assert response.json() == USERNAME_IN_USE_MSG(user_already_exists["username"])


def test_editing_email_to_used_value_returns_409(users, edit_user):
    """Alice troca seu email para Bernardo@gmail.com"""

    user_edit = users["Alice"].copy()
    user_already_exists = users["Bernardo"]

    user_edit["email"] = user_already_exists["email"]

    response = edit_user(user_edit)
    assert response.status_code == 409,  response.json()
    assert response.json() == EMAIL_IN_USE_MSG(user_already_exists["email"])


def test_editing_user_bio_returns_200(users, edit_user):
    """Alice coloca uma bio na sua conta"""

    user = users["Alice"]
    user_edit = user.copy()
    user_edit["bio"] = "Alice " * 10 + "."

    response = edit_user(user_edit, user)
    assert response.status_code == 200,  response.json()
    assert response.json()["bio"] == user_edit["bio"]


def test_editing_user_bio_to_too_large_returns_400(users, edit_user):
    """Alice coloca uma bio muito grande na sua conta"""

    user_edit = users["Alice"].copy()
    user_edit["bio"] = "Alice"* 80 + "."

    response = edit_user(user_edit)
    assert response.status_code == 400,  response.json()
    assert response.json() == {"message": "A bio não pode ter mais que 280 caractéres!"}


def test_editing_user_bio_to_empty_returns_400(users, edit_user):
    """Alice coloca uma bio muito grande na sua conta, e depois uma bio vazia"""

    user_edit = users["Alice"].copy()
    user_edit["bio"] = "       "

    response = edit_user(user_edit)
    assert response.status_code == 400,  response.json()
    assert response.json() == {"message": "A bio não pode ser apenas espaço vazio!"}

