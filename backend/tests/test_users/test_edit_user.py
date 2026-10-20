from .utils import *


def test_editing_username_to_unused_returns_200(users, edit_user_request):
    """Alice troca o seu username para Joao"""

    user = users["Alice"]
    edited_user = copy.copy(user)
    edited_user.username = "Joao"

    response = edit_user_request(edited_user, user)
    assert response.status_code == 200, response.json()
    assert response.json()["username"] == edited_user.username, response.json()


def test_editing_username_to_too_short_returns_400(users, edit_user_request):
    """Alice troca o seu username para um valor muito curto"""

    edited_user = copy.copy(users["Alice"])
    edited_user.username = "Ali"

    response = edit_user_request(edited_user)
    assert response.status_code == 400,  response.json()
    assert response.json() == USERNAME_WRONG_LENGTH_MSG, response.json()


def test_editing_username_to_too_long_returns_400(users, edit_user_request):
    """Alice troca o seu username para um valor muito longo"""

    edited_user = copy.copy(users["Alice"])
    edited_user.username = "Alice" * 20 

    response = edit_user_request(edited_user)
    assert response.status_code == 400, response.json()
    assert response.json() == USERNAME_WRONG_LENGTH_MSG, response.json()


def test_editing_user_info_to_unused_values_returns_200(users, edit_user_request):
    """Alice troca o seu username para Joao e seu email para Joao@gmail.com"""

    user = users["Alice"]
    edited_user = copy.copy(user)

    edited_user.username = "Joao"
    edited_user.email = "Joao@gmail.com"

    response = edit_user_request(edited_user, user)
    assert response.status_code == 200, response.json()
    assert response.json()["username"] == edited_user.username, response.json()


def test_editing_username_to_used_value_returns_409(users, edit_user_request):
    """Alice troca seu username para Bernardo"""

    user_edit = copy.copy(users["Alice"])
    user_already_exists = users["Bernardo"]

    user_edit.username = user_already_exists.username

    response = edit_user_request(user_edit)
    assert response.status_code == 409, response.json()
    assert response.json() == USERNAME_IN_USE_MSG(user_already_exists.username), response.json()


def test_editing_user_bio_returns_200(users, edit_user_request):
    """Alice coloca uma bio na sua conta"""

    user = users["Alice"]
    user_edit = copy.copy(user)
    user_edit.bio = "Alice " * 10

    response = edit_user_request(user_edit, user)
    assert response.status_code == 200,  response.json()
    assert response.json()["bio"] == user_edit.bio, response.json()


def test_editing_user_bio_to_too_large_returns_400(users, edit_user_request):
    """Alice coloca uma bio muito grande na sua conta"""

    user_edit = copy.copy(users["Alice"])
    user_edit.bio = "Alice"*80 + "."

    response = edit_user_request(user_edit)
    assert response.status_code == 400,  response.json()
    assert response.json() == BIO_WRONG_LENGTH_MSG, response.json()


def test_editing_user_bio_to_empty_returns_400(users, edit_user_request):
    """Alice coloca uma bio muito grande na sua conta, e depois uma bio vazia"""

    user_edit = copy.copy(users["Alice"])
    user_edit.bio = "       "

    response = edit_user_request(user_edit)
    assert response.status_code == 400,  response.json()
    assert response.json() == EMPTY_BIO_MSG, response.json()

