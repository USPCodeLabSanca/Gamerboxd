from .utils import *

BIO_WRONG_LENGTH_MSG = {"message": "A bio não pode ter mais que 280 caracteres!"}
BIO_EMPTY_MSG = {"message": "A bio não pode ser apenas espaço vazio!"}

@pytest.mark.parametrize("username, expected_status, expected_json", [
    ("Joao Lucas", 200, None),
    ("Joao      ", 200, None),
    ("Alice_"*4, 200, None),
    ("Bernardo", 409, USERNAME_IN_USE_MSG("Bernardo")),
    ("Alice"*20, 400, USERNAME_WRONG_LENGTH_MSG),
    ("A", 400, USERNAME_WRONG_LENGTH_MSG)
])
def test_editing_username_checks_edge_cases(users, edit_user_request, username, expected_status, expected_json):
    """Alice troca o seu username"""

    user = users["Alice"]
    edited_user = copy.copy(user)
    edited_user.username = username

    response = edit_user_request(edited_user, user)
    assert response.status_code == expected_status, response.json()

    if expected_json is None:
        assert response.json()["username"].strip() == edited_user.username.strip()

    else:
        assert response.json() == expected_json


@pytest.mark.parametrize("bio, expected_status, expected_json", [
    ("Gosto de games de ação e cartas!", 200, None),
    ("Gosto de games de ação!         ", 200, None),
    ("Games"*56, 200, None),
    ("Alice"*61, 400, BIO_WRONG_LENGTH_MSG),
    ("        ", 400, BIO_EMPTY_MSG)
])
def test_editing_bio(users, edit_user_request, bio, expected_status, expected_json):
    """Alice coloca uma bio na sua conta"""

    user = users["Alice"]
    user_edit = copy.copy(user)
    user_edit.bio = bio

    response = edit_user_request(user_edit, user)
    assert response.status_code == expected_status, response.json()

    if expected_json is None:
        assert response.json()["bio"].strip() == user_edit.bio.strip()

    else:
        assert response.json() == expected_json
