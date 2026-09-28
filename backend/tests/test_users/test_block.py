from .utils import *

# users é um fixture definido em tests/conftest.py
# block é um fixture definido em tests/conftest.py
# unblock é um fixture definido em tests/conftest.py
# follow é um fixture definido em tests/conftest.py

def test_blocking_returns_200(users, block):
    """Alice bloqueia Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = block(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_BLOCKING_MSG
    assert_block(user1, user2)


def test_unblocking_returns_200(users, unblock):
    """Alice desbloqueia Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = unblock(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_UNBLOCKING_MSG
    assert_unblock(user1, user2)


def test_blocking_twice_returns_200_twice(users, block):
    """Alice bloqueia Bernardo 2 vezes"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = block(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_block(user1, user2)

    response = block(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert_block(user1, user2)


def test_unblocking_someone_not_blocked_returns_200(users, unblock):
    """Alice desbloqueia Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = unblock(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_unblock(user1, user2)


def test_blocking_someone_that_doenst_exist_returns_404(users, block):
    """Alice bloqueia inexistente"""

    user1, inexistent = users["Alice"], {"username": "inexistente"}

    response = block(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_unblocking_someone_that_doenst_exist_returns_404(users, unblock):
    """Alice desbloqueia inexistente"""

    user1, inexistent = users["Alice"], {"username": "inexistente"}

    response = unblock(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_block_yourself_returns_403(users, block):
    """Alice bloqueia Alice"""

    user1 = users["Alice"]

    response = block(user1, user1, False)
    assert response.status_code == 403, response.json()
    assert response.json() == {"message":"O usuário não pode bloquear a si mesmo!"}
    assert_unblock(user1, user1)


def test_blocking_stops_follow(users, block, follow):
    """Alice bloqueia Bernardo, Bernardo segue Alice"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = block(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert_block(user1, user2)

    user1, user2 = user2, user1

    response = follow(user1, user2, False)
    assert response.status_code == 403, response.json()
    assert response.json() == {"message":"O usuário está tentando seguir alguém que o bloqueou!"}
    assert_unfollow(user1, user2)


def test_blocking_removes_follow(users, follow, block):
    """Alice segue Bernardo, Bernardo bloqueia Alice"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)

    user1, user2 = user2, user1

    response = block(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert_block(user1, user2)
    assert_unfollow(user2, user1)


    


