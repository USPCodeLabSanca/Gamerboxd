from . import *
from .test_follow import follow, assert_follow, assert_unfollow


def block(atv: dict, pas: dict):
    """Roda o bloqueio no backend"""

    target, cookies = pas["username"], atv["cookies"]
    return requests.post(f"{BASE_URL}/block/{target}", cookies=cookies)

def unblock(atv: dict, pas: dict):
    """Roda o desbloqueio no backend"""

    target, cookies = pas["username"], atv["cookies"]
    return requests.delete(f"{BASE_URL}/block/{target}", cookies=cookies)

def view_block(atv: dict):
    cookies = atv["cookies"]
    response = requests.get(f"{BASE_URL}/block", cookies=cookies)
    return response.json()

def assert_block(atv: dict, pas: dict):
    """Garante que atv bloqueou pas"""

    response_json = view_block(atv)
    assert any([f["username"] == pas["username"] for f in response_json["blocks"]])

def assert_unblock(atv: dict, pas: dict):
    """Garante que atv não bloqueou pas"""

    response_json = view_block(atv) 
    assert all([f["username"] != pas["username"] for f in response_json["blocks"]])


# ========= Testes ===========

def test_block(users):
    """Alice bloqueia e depois desbloqueia Bernardo"""

    atv, pas= users["Alice"], users["Bernardo"]

    response = block(atv, pas)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_BLOCKING_MSG
    assert_block(atv, pas)

    response = unblock(atv, pas)
    assert response.status_code == 200
    assert response.json() == SUCCESS_UNBLOCKING_MSG
    assert_unblock(atv, pas)


def test_block_twice(users):
    """Bernardo bloqueia Caua 2 vezes"""

    atv, pas = users["Bernardo"], users["Caua"]

    response = block(atv, pas)
    assert response.status_code == 200
    assert response.json() == SUCCESS_BLOCKING_MSG
    assert_block(atv, pas)

    response = block(atv, pas)
    assert response.status_code == 200, f"{response.json()}"
    assert response.json() == SUCCESS_BLOCKING_MSG
    assert_block(atv, pas)


def test_unblock_someone_not_blocked(users):
    """Caua desbloqueia Daniela"""

    atv, pas = users["Caua"], users["Daniela"]

    response = unblock(atv, pas)
    assert response.status_code == 200
    assert response.json() == SUCCESS_UNBLOCKING_MSG
    assert_unblock(atv, pas)


def test_block_someone_that_doenst_exist(users):
    """Daniela bloqueia e desbloqueia inexistente"""

    atv, inexistent = users["Daniela"], {"username": "inexistente"}

    response = block(atv, inexistent)
    assert response.status_code == 404
    assert response.json() == USER_NOT_FOUND_MSG

    response = unblock(atv, inexistent)
    assert response.status_code == 404
    assert response.json() == USER_NOT_FOUND_MSG


def test_block_yourself(users):
    """Eduarda bloqueia Eduarda"""

    atv, pas = users["Eduarda"], users["Eduarda"]

    response = block(atv, pas)
    assert response.status_code == 403
    assert response.json() == {"message":"O usuário não pode bloquear a si mesmo!"}
    assert_unblock(atv, pas)


def test_block_stops_follow(users):
    """Fabio bloqueia Gabriela, Gabriela segue Fabio"""

    atv, pas = users["Fabio"], users["Gabriela"]

    response = block(atv, pas)
    assert response.status_code == 200
    assert response.json() == SUCCESS_BLOCKING_MSG
    assert_block(atv, pas)

    atv, pas = pas, atv

    response = follow(atv, pas)
    assert response.status_code == 403
    assert response.json() == {"message":"O usuário está tentando seguir alguém que o bloqueou!"}
    assert_unfollow(atv, pas)


def test_block_undoes_follow(users):
    """Helio segue Iara, Iara bloqueia Helio"""

    atv, pas = users["Helio"], users["Iara"]

    response = follow(atv, pas)
    assert response.status_code == 200
    assert response.json() == SUCCESS_FOLOWING_MSG
    assert_follow(atv, pas)

    atv, pas = pas, atv

    response = block(atv, pas)
    assert response.status_code == 200
    assert response.json() == SUCCESS_BLOCKING_MSG
    assert_block(atv, pas)
    assert_unfollow(pas, atv)


    


