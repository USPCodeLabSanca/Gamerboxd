from . import BASE_URL, pytest, requests
from .test_follow import follow, assert_follow, assert_unfollow


def block(atv: dict, pas: dict):
    target, cookies = pas["username"], atv["cookies"]
    return requests.post(f"{BASE_URL}/block/{target}", cookies=cookies)

def unblock(atv: dict, pas: dict):
    target, cookies = pas["username"], atv["cookies"]
    return requests.delete(f"{BASE_URL}/block/{target}", cookies=cookies)

def view_block(atv: dict):
    cookies = atv["cookies"]
    return requests.get(f"{BASE_URL}/block", cookies=cookies)

def assert_block(atv: dict, pas: dict):
    """Garante que atv bloqueou pas"""
    response = view_block(atv)   
    assert any([f["username"] == pas["username"] for f in response.json()["blockeds"]])

def assert_unblock(atv: dict, pas: dict):
    """Garante que atv não bloqueou pas"""
    response = view_block(atv) 
    assert all([f["username"] != pas["username"] for f in response.json()["blockeds"]])


def test_block(users):
    """Alice bloqueia e depois desbloqueia Bernardo"""

    response = block(users["Alice"], users["Bernardo"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta bloqueada com sucesso!"}
    assert_block(users["Alice"], users["Bernardo"])

    response = unblock(users["Alice"], users["Bernardo"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta desbloqueada com sucesso!"}
    assert_unblock(users["Alice"], users["Bernardo"])


def test_block_twice(users):
    """Bernardo bloqueia Caua 2 vezes"""

    response = block(users["Bernardo"], users["Caua"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta bloqueada com sucesso!"}
    assert_block(users["Bernardo"], users["Caua"])

    response = block(users["Bernardo"], users["Caua"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta bloqueada com sucesso!"}
    assert_block(users["Bernardo"], users["Caua"])


def test_unblock_someone_not_blocked(users):
    """Caua desbloqueia Daniela"""

    response = unblock(users["Caua"], users["Daniela"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta desbloqueada com sucesso!"}
    assert_unblock(users["Caua"], users["Daniela"])


def test_block_someone_that_doenst_exist(users):
    """Daniela bloqueia e desbloqueia inexistente"""

    inexistent = {"username": "inexistente"}

    response = block(users["Daniela"], inexistent)
    assert response.status_code == 404
    assert response.json() == {"message":"Usuário não encontrado!"}

    response = unblock(users["Daniela"], inexistent)
    assert response.status_code == 404
    assert response.json() == {"message":"Usuário não encontrado!"}


def test_block_yourself(users):
    """Eduarda bloqueia Eduarda"""

    response = block(users["Eduarda"], users["Eduarda"])
    assert response.status_code == 403
    assert response.json() == {"message":"O usuário não pode bloquear a si mesmo!"}
    assert_unblock(users["Eduarda"], users["Eduarda"])


def test_block_stops_follow(users):
    """Fabio bloqueia Gabriela, Gabriela segue Fabio"""

    response = block(users["Fabio"], users["Gabriela"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta bloqueada com sucesso!"}
    assert_block(users["Fabio"], users["Gabriela"])

    response = follow(users["Gabriela"], users["Fabio"])
    assert response.status_code == 403, f"{response.json()}"
    assert response.json() == {"message":"O usuário está bloqueado por quem ele está tentando seguir!"}
    assert_unfollow(users["Gabriela"], users["Fabio"])


def test_block_undoes_follow(users):
    """Helio segue Iara, Iara bloqueia Helio"""

    response = follow(users["Helio"], users["Iara"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta seguida com sucesso!"}
    assert_follow(users["Helio"], users["Iara"])

    response = block(users["Iara"], users["Helio"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta bloqueada com sucesso!"}
    assert_block(users["Iara"], users["Helio"])
    assert_unfollow(users["Helio"], users["Iara"])


    


