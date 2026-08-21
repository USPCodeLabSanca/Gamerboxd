from . import BASE_URL, pytest, requests

def create_account(username):
    payload = {"username": username, "password": f"{username}{username}1!", "email": f"{username}@gmail.com"}

    session = requests.Session()
    response = session.post(BASE_URL + "/user", json=payload)

    for cookie in session.cookies:
        cookie.secure = False

    assert response.status_code == 200
    assert response.json() == {"message":"Conta criada com sucesso!"}

    return {**payload, "cookies": session.cookies}


def delete_accounts(users: dict):

    for user in users.values():
        session = requests.Session()
        response = session.delete(BASE_URL + "/user", cookies=user["cookies"])

        assert response.status_code == 200
        assert response.json() == {"message":"Conta deletada com sucesso!"}


@pytest.fixture(scope='module')
def users():
    users = {
        "Alice": create_account("Alice"),
        "Bernardo": create_account("Bernardo"),
        "Caua": create_account("Caua"),
        "Daniela" :create_account("Daniela"),
        "Eduarda": create_account("Eduarda"),
        "Fabio": create_account("Fabio"),
        "Gabriela": create_account("Gabriela"),
        "Helio": create_account("Helio"),
        "Iara": create_account("Iara")
    }

    yield users

    #delete_accounts(users)





