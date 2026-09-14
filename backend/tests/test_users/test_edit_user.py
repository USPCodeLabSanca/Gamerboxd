from . import BASE_URL, pytest, requests


def edit_account(user: dict):
    user_without_cookies = user.copy()
    cookies = user_without_cookies.pop("cookies", None)

    return requests.put(f"{BASE_URL}", cookies=cookies, json=user_without_cookies)


# ========= Testes ===========

def test_edit_user_to_not_used_one(users):
    """Alice troca o seu username para João, e o seu email para Joao@gmail.com"""

    user = users["Alice"]

    user["username"] = "Joao"

    response = edit_account(user)
    assert response.status_code == 200, f"{response.json()}"

    user["email"] = "Joao@gmail.com"

    response = edit_account(user)
    assert response.status_code == 200


def test_edit_user_to_used_one(users):
    """Bernardo troca seu username para Caua, e o seu email para Caua@gmail.com"""

    user = users["Bernardo"]
    user_already_exists = users["Caua"]

    user["username"] = user_already_exists["username"]

    response = edit_account(user)
    assert response.status_code == 409
    assert response.json() == {"message": f'O username "{user_already_exists["username"]}" já está sendo utilizado!'}

    user["username"] = "Bernardo"
    user["email"] = user_already_exists["email"]

    response = edit_account(user)
    assert response.status_code == 409
    assert response.json() == {"message": f'O email "{user_already_exists["email"]}" já está sendo utilizado!'}


def test_edit_user_bio(users):
    """Daniela coloca uma bio na sua conta"""

    user = users["Daniela"]

    user["bio"] = "Daniela " * 10 + "."

    response = edit_account(user)
    assert response.status_code == 200
    assert response.json()["bio"] == user["bio"]


def test_edit_user_bio_out_of_bounds(users):
    """Eduarda coloca uma bio muito grande na sua conta, e uma bio vazia"""

    user = users["Eduarda"]
    user["bio"] = "Eduarda" * 40 + "."

    response = edit_account(user)
    assert response.status_code == 400
    assert response.json() == {"message": "A bio não pode ter mais que 280 caractéres!"}

    user["bio"] = "       "

    response = edit_account(user)
    assert response.status_code == 400
    assert response.json() == {"message": "A bio não pode ser apenas espaço vazio!"}




