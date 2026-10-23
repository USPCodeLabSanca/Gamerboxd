from math import ceil
from .utils import *


SUCCESS_BLOCKING_MSG = {"message":"Conta bloqueada com sucesso!"}
SUCCESS_UNBLOCKING_MSG = {"message":"Conta desbloqueada com sucesso!"}
CANT_BLOCK_YOURSELF_MSG = {"message":"O usuário não pode bloquear a si mesmo!"}
FOLLOW_SOMEONE_WHO_BLOCKED_YOU_MSG = {"message":"O usuário está tentando seguir alguém que o bloqueou!"}
FOLLOW_SOMEONE_WHO_YOUVE_BLOCKED_MSG = {"message": "Não é possível ver detalhes de um usuário antes de desbloqueá-lo!"}


def test_blocking_returns_200(users, block_request):
    """Alice bloqueia Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = block_request(user1, user2)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_BLOCKING_MSG
    assert_block(user1, user2)


def test_unblocking_returns_200(users, block_request, unblock_request):
    """Alice desbloqueia Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    block_resp = block_request(user1, user2, False)
    assert block_resp.status_code == 200, response.json()

    response = unblock_request(user1, user2)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_UNBLOCKING_MSG
    assert_unblock(user1, user2)


def test_blocking_twice_returns_200_twice(users, block_request):
    """Alice bloqueia Bernardo 2 vezes"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = block_request(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_block(user1, user2)

    response = block_request(user1, user2)
    assert response.status_code == 200, response.json()
    assert_block(user1, user2)


def test_unblocking_someone_not_blocked_returns_200(users, unblock_request):
    """Alice desbloqueia Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = unblock_request(user1, user2)
    assert response.status_code == 200, response.json()
    assert_unblock(user1, user2)


def test_blocking_someone_that_doenst_exist_returns_404(users, block_request):
    """Alice bloqueia inexistente"""

    user1, inexistent = users["Alice"], BaseUser(user_id="inexistente")

    response = block_request(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_unblocking_someone_that_doenst_exist_returns_404(users, unblock_request):
    """Alice desbloqueia inexistente"""

    user1, inexistent = users["Alice"], BaseUser(user_id="inexistente")

    response = unblock_request(user1, inexistent)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_block_yourself_returns_403(users, block_request):
    """Alice bloqueia Alice"""

    user1 = users["Alice"]

    response = block_request(user1, user1, False)
    assert response.status_code == 403, response.json()
    assert response.json() == CANT_BLOCK_YOURSELF_MSG
    assert_unblock(user1, user1)


def test_blocking_stops_follow_both_ways(users, block_request, follow_request):
    """Alice bloqueia Bernardo, Bernardo segue Alice"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = block_request(user1, user2)
    assert response.status_code == 200, response.json()
    assert_block(user1, user2)

    response = follow_request(user2, user1, False)
    assert response.status_code == 403, response.json()
    assert response.json() == FOLLOW_SOMEONE_WHO_BLOCKED_YOU_MSG
    assert_unfollow(user2, user1)

    response = follow_request(user1, user2, False)
    assert response.status_code == 409, response.json()
    assert response.json() == FOLLOW_SOMEONE_WHO_YOUVE_BLOCKED_MSG
    assert_unfollow(user1, user2)


def test_blocking_removes_follow_both_ways(users, follow_request, block_request):
    """Alice segue Bernardo, Bernardo bloqueia Alice"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow_request(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)

    response = follow_request(user2, user1, False)
    assert response.status_code == 200, response.json()
    assert_follow(user2, user1)

    response = block_request(user2, user1)
    assert response.status_code == 200, response.json()
    assert_block(user2, user1)
    assert_unfollow(user1, user2)





