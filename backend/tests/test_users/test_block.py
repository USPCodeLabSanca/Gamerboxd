import pytest
import requests

from ..utils import BASE_URL_USERS, BaseUser, assert_block, assert_unblock, USER_NOT_FOUND_MSG, NOT_LOGGED_IN_MSG

SUCCESS_BLOCKING_MSG = {"message":"Conta bloqueada com sucesso!"}
SUCCESS_UNBLOCKING_MSG = {"message":"Conta desbloqueada com sucesso!"}
CANT_BLOCK_YOURSELF_MSG = {"message":"O usuário não pode bloquear a si mesmo!"}


def test_blocking_returns_200(users, block_request):
    """Alice bloqueia Bernardo"""

    blocker, blocked = users("Alice"), users("Bernardo")

    response = block_request(blocker, blocked)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_BLOCKING_MSG
    assert_block(blocker, blocked)


def test_unblocking_returns_200(users, block_request, unblock_request):
    """Alice desbloqueia Bernardo"""

    blocker, blocked = users("Alice"), users("Bernardo")

    response = block_request(blocker, blocked, False)
    assert response.status_code == 200, response.json()

    response = unblock_request(blocker, blocked)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_UNBLOCKING_MSG
    assert_unblock(blocker, blocked)


def test_blocking_twice_returns_200_twice(users, block_request):
    """Alice bloqueia Bernardo 2 vezes"""

    blocker, blocked = users("Alice"), users("Bernardo")

    response = block_request(blocker, blocked, False)
    assert response.status_code == 200, response.json()
    assert_block(blocker, blocked)

    response = block_request(blocker, blocked)
    assert response.status_code == 200, response.json()
    assert_block(blocker, blocked)


def test_unblocking_someone_not_blocked_returns_200(users, unblock_request):
    """Alice desbloqueia Bernardo"""

    blocker, blocked = users("Alice"), users("Bernardo")

    response = unblock_request(blocker, blocked)
    assert response.status_code == 200, response.json()
    assert_unblock(blocker, blocked)


def test_blocking_someone_that_doenst_exist_returns_404(users, block_request):
    """Alice tenta bloquear inexistente"""

    blocker, inexistent = users("Alice"), BaseUser(user_id="inexistente")

    response = block_request(blocker, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_unblocking_someone_that_doenst_exist_returns_404(users, unblock_request):
    """Alice tenta desbloquear inexistente"""

    unblocker, inexistent = users("Alice"), BaseUser(user_id="inexistente")

    response = unblock_request(unblocker, inexistent)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_blocking_while_not_logged_in_returns_401(users):
    """Um usuário tenta bloquear Alice sem enviar os seus cookies de autenticação"""

    blocked = users("Alice")
    response = requests.post(BASE_URL_USERS + f"/block/{blocked.user_id}")
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG


def test_unblocking_while_not_logged_in_returns_401(users):
    """Um usuário tenta desbloquear Alice sem enviar os seus cookies de autenticação"""

    unblocked = users("Alice")
    response = requests.delete(BASE_URL_USERS + f"/block/{unblocked.user_id}")
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG


def test_blocking_yourself_returns_403(users, block_request):
    """Alice tenta bloquear Alice"""

    user = users("Alice")

    response = block_request(user, user, False)
    assert response.status_code == 403, response.json()
    assert response.json() == CANT_BLOCK_YOURSELF_MSG
    assert_unblock(user, user)


def test_block_pagination(pagination_tests, users, create_account, block_request):
    """Alice bloqueia vários usuários"""

    def seed(blocker: BaseUser, total: int, order: str = "", search: str = None):
        """Cria vários usuários diferentes e faz o blocker bloquear eles"""

        usernames = [f"User{i+1}" for i in range(total)] if search is None else [(search + "_" * i) for i in range(total)]

        for u in usernames:
            blocked = create_account(u)
            response = block_request(blocker, blocked, cleanup=False)
            assert response.status_code == 200, response.json()

        if ("!" in order) or (len(order) == 0):
            usernames.reverse()

        return usernames

    seed.cleanup = create_account.cleanup
    seed.expected_content = ["user_id", "username", "pfp"]
    seed.valid_orders = ["created_at", "username"]
    seed.searches = ["Alex", "Beto", "Carla"]
    seed.return_obj = "username"

    pagination_tests(
        user = users("Alice"),
        url = BASE_URL_USERS + "/block",
        seed = seed,
        require_login = True
    )





