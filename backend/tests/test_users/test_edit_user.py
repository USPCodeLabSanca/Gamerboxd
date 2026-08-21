from . import BASE_URL, pytest, requests

def edit_account(user: dict):
    user_without_cookies = user.copy()
    cookies = user_without_cookies.pop("cookies", None)

    return requests.put(f"{BASE_URL}/user", cookies=cookies, json=user_without_cookies)


def test_edit_user_to_not_used_one(users):
    """ALice troca o seu username para João, e o seu email para Joao@gmail.com"""

    users["Alice"]["username"] = "Joao"

    response = edit_account(users["Alice"])
    assert response.status_code == 200, f"{response.json()}"

    users["Alice"]["email"] = "Joao@gmail.com"

    response = edit_account(users["Alice"])
    assert response.status_code == 200


def test_edit_user_to_used_one(users):
    """Bernardo troca seu username para Caua, e o seu email para Caua@gmail.com"""

    users["Bernardo"]["username"] = "Caua"

    response = edit_account(users["Bernardo"])
    assert response.status_code == 409
    assert response.json() == {"message": 'O username "Caua" já está sendo utilizado!'}

    users["Bernardo"]["username"] = "Bernardo"
    users["Bernardo"]["email"] = "Caua@gmail.com"

    response = edit_account(users["Bernardo"])
    assert response.status_code == 409
    assert response.json() == {"message": 'O email "Caua@gmail.com" já está sendo utilizado!'}


def test_edit_user_bio(users):
    """Daniela coloca uma bio na sua conta"""

    users["Daniela"]["bio"] = "Daniela " * 10 + "."

    response = edit_account(users["Daniela"])
    assert response.status_code == 200
    assert response.json()["bio"] == users["Daniela"]["bio"]


def test_edit_user_bio_out_of_bounds(users):
    """Eduarda coloca uma bio muito grande na sua conta, e uma bio vazia"""

    users["Eduarda"]["bio"] = "Eduarda" * 40 + "."

    response = edit_account(users["Eduarda"])
    assert response.status_code == 400
    assert response.json() == {"message": "A bio não pode ter mais que 280 caractéres!"}

    users["Eduarda"]["bio"] = "       "

    response = edit_account(users["Eduarda"])
    assert response.status_code == 400
    assert response.json() == {"message": "A bio não pode ser apenas espaço vazio!"}




