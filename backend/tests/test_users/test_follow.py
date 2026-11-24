import pytest
import requests

from ..utils import BASE_URL_USERS, BaseUser, assert_follow, assert_unfollow, USER_NOT_FOUND_MSG, NOT_LOGGED_IN_MSG

SUCCESS_FOLLOWING_MSG = {"message":"Conta seguida com sucesso!"}
SUCCESS_UNFOLLOWING_MSG = {"message":"Conta desseguida com sucesso!"}
CANT_FOLLOW_YOURSELF_MSG = {"message":"O usuário não pode seguir a si mesmo!"}
FOLLOW_SOMEONE_WHO_BLOCKED_YOU_MSG = {"message":"O usuário está tentando ver detalhes da conta de alguém que o bloqueou!"}
FOLLOW_SOMEONE_WHO_YOUVE_BLOCKED_MSG = {"message": "Não é possível ver detalhes de um usuário antes de desbloqueá-lo!"}

def test_follow_returns_200(users, follow_request):
    """Alice segue Bernardo"""

    follower, followed = users("Alice"), users("Bernardo")

    response = follow_request(follower, followed)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_FOLLOWING_MSG
    assert_follow(follower, followed)


def test_unfollow_returns_200(users, follow_request, unfollow_request):
    """Alice segue e dessegue Bernardo"""

    follower, followed = users("Alice"), users("Bernardo")

    response = follow_request(follower, followed, False)
    assert response.status_code == 200, response.json()

    response = unfollow_request(follower, followed)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_UNFOLLOWING_MSG
    assert_unfollow(follower, followed)


def test_follow_twice_returns_200_twice(users, follow_request):
    """Alice segue Bernardo 2 vezes"""

    follower, followed = users("Alice"), users("Bernardo")

    response = follow_request(follower, followed, False)
    assert response.status_code == 200, response.json()
    assert_follow(follower, followed)

    response = follow_request(follower, followed)
    assert response.status_code == 200, response.json()
    assert_follow(follower, followed)


def test_unfollow_someone_not_followed_returns_200(users, unfollow_request):
    """Alice dessegue Bernardo sem antes segui-lo"""

    unfollower, unfollowed = users("Alice"), users("Bernardo")

    response = unfollow_request(unfollower, unfollowed)
    assert response.status_code == 200, response.json()
    assert_unfollow(unfollower, unfollowed)


def test_follow_someone_that_doenst_exist_returns_404(users, follow_request):
    """Alice tenta seguir inexistente"""

    user, inexistent = users("Alice"), BaseUser(user_id="inexistente")

    response = follow_request(user, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_unfollow_someone_that_doenst_exist_returns_404(users, unfollow_request):
    """Alice tenta desseguir inexistente"""

    user, inexistent = users("Alice"), BaseUser(user_id="inexistente")
    
    response = unfollow_request(user, inexistent)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_following_yourself_returns_403(users, follow_request):
    """Alice tenta seguir Alice"""

    user = users("Alice")
    response = follow_request(user, user, False)
    assert response.status_code == 403, response.json()
    assert response.json() == CANT_FOLLOW_YOURSELF_MSG
    assert_unfollow(user, user)


def test_following_while_not_logged_in_returns_401(users):
    """Um usuário tenta seguir o outro sem enviar os seus cookies de autenticação"""

    followed = users("Alice")
    response = requests.post(BASE_URL_USERS + f"/follow/{followed.user_id}")
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG


def test_unfollowing_while_not_logged_in_returns_401(users):
    """Um usuário tenta desseguir o outro sem enviar os seus cookies de autenticação"""

    unfollowed = users("Alice")
    response = requests.delete(BASE_URL_USERS + f"/follow/{unfollowed.user_id}")
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG


def test_blocking_stops_follow_both_ways(users, block_request, follow_request):
    """Alice bloqueia Bernardo, Bernardo tenta seguir Alice, Alice tenta seguir Bernardo"""

    blocker, blocked = users("Alice"), users("Bernardo")

    response = block_request(blocker, blocked)
    assert response.status_code == 200, response.json()

    response = follow_request(blocked, blocker, False)
    assert response.status_code == 433, response.json()
    assert response.json() == FOLLOW_SOMEONE_WHO_BLOCKED_YOU_MSG
    assert_unfollow(blocked, blocker)

    response = follow_request(blocker, blocked, False)
    assert response.status_code == 400, response.json()
    assert response.json() == FOLLOW_SOMEONE_WHO_YOUVE_BLOCKED_MSG
    assert_unfollow(blocker, blocked)


def test_blocking_removes_follow_both_ways(users, follow_request, block_request):
    """Alice segue Bernardo, Bernardo bloqueia Alice"""

    blocked, blocker = users("Alice"), users("Bernardo")

    response = follow_request(blocked, blocker, False)
    assert response.status_code == 200, response.json()

    response = follow_request(blocker, blocked, False)
    assert response.status_code == 200, response.json()

    response = block_request(blocker, blocked)
    assert response.status_code == 200, response.json()
    assert_unfollow(blocked, blocker)
    assert_unfollow(blocker, blocked)


@pytest.mark.parametrize("direction", ["followers", "followings"])
def test_follow_pagination(direction, pagination_tests, users, create_account, follow_request):
    """Vários usuários seguem Alice (direction = followers) ou Alice segue vários usuários (direction = followings)"""

    def seed(main_user: BaseUser, total: int, order: str = "", search: str = None):
        """Cria vários usuários diferentes e faz eles serem seguidos pelo main_user ou faz eles seguirem o main user"""

        usernames = [f"User{i+1}" for i in range(total)] if search is None else [(search + "_" * i) for i in range(total)]

        for u in usernames:
            other_user = create_account(u)
            args = (other_user, main_user) if "r" in direction else (main_user, other_user)
            response = follow_request(*args, cleanup=False)
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
        url = BASE_URL_USERS + f"/follow/{direction}/{users("Alice").user_id}",
        seed = seed,
        require_login = True
    )
