from .utils import *

SUCCESS_FOLLOWING_MSG = {"message":"Conta seguida com sucesso!"}
SUCCESS_UNFOLLOWING_MSG = {"message":"Conta desseguida com sucesso!"}
CANT_FOLLOW_YOURSELF_MSG = {"message":"O usuário não pode seguir a si mesmo!"}

def test_follow_returns_200(users, follow_request):
    """Alice segue Bernardo"""

    follower, followed = users["Alice"], users["Bernardo"]

    response = follow_request(follower, followed)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_FOLLOWING_MSG
    assert_follow(follower, followed)


def test_unfollow_returns_200(users, follow_request, unfollow_request):
    """Alice segue e dessegue Bernardo"""

    follower, followed = users["Alice"], users["Bernardo"]

    response = follow_request(follower, followed, False)
    assert response.status_code == 200, response.json()

    response = unfollow_request(follower, followed)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_UNFOLLOWING_MSG
    assert_unfollow(follower, followed)


def test_follow_twice_returns_200_twice(users, follow_request):
    """Alice segue Bernardo 2 vezes"""

    follower, followed = users["Alice"], users["Bernardo"]

    response = follow_request(follower, followed, False)
    assert response.status_code == 200, response.json()
    assert_follow(follower, followed)

    response = follow_request(follower, followed)
    assert response.status_code == 200, response.json()
    assert_follow(follower, followed)


def test_unfollow_someone_not_followed_returns_200(users, unfollow_request):
    """Alice dessegue Bernardo sem antes segui-lo"""

    unfollower, unfollowed = users["Alice"], users["Bernardo"]

    response = unfollow_request(unfollower, unfollowed)
    assert response.status_code == 200, response.json()
    assert_unfollow(unfollower, unfollowed)


def test_follow_someone_that_doenst_exist_returns_404(users, follow_request):
    """Alice segue inexistente"""

    user, inexistent = users["Alice"], BaseUser(user_id = "inexistente")

    response = follow_request(user, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_unfollow_someone_that_doenst_exist_returns_404(users, unfollow_request):
    """Alice dessegue inexistente"""

    user, inexistent = users["Alice"], BaseUser(user_id = "inexistente")
    
    response = unfollow_request(user, inexistent)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_following_yourself_returns_403(users, follow_request):
    """Alice segue Alice"""

    user = users["Alice"]

    response = follow_request(user, user, False)
    assert response.status_code == 403, response.json()
    assert response.json() == CANT_FOLLOW_YOURSELF_MSG
    assert_unfollow(user, user)


@pytest.mark.slow
def test_followers_pagination(pagination_tests, users, create_account, follow_request):
    """Vários usuários seguem Alice"""

    def seed_order(followed: BaseUser, total: int, order: str = ""):
        """Cria vários usuários diferentes e faz eles seguirem o followed, em ordens diferentes"""

        usernames = [f"User{i+1}" for i in range(total)]
        create_account.cleanup()

        for u in usernames:
            follower = create_account(u)
            response = follow_request(follower, followed, cleanup=False)
            assert response.status_code == 200, response.json()

        if "!" in order:
            usernames.reverse()

        return usernames


    def seed_search(followed: BaseUser, total: int, search: str):
        """Cria vários usuários diferentes e faz eles seguirem o followed, para que alguns apareçam no search depois"""

        searched_usernames = [ (search + "_" * i) for i in range(total)]
        unsearched_usernames = ["Joao", "Maria"]
        all_usernames = searched_usernames + unsearched_usernames
        create_account.cleanup()

        for u in all_usernames:
            follower = create_account(u)
            response = follow_request(follower, followed, cleanup=False)
            assert response.status_code == 200, response.json()

        searched_usernames.reverse()

        return {"match": searched_usernames, "no_match": unsearched_usernames}

    pagination_tests(
        user = users["Alice"],
        url = BASE_URL_USERS + f"/follow/followers/{users["Alice"].user_id}",
        seed_order = seed_order,
        seed_search = seed_search,
        seed_obj = "username",
        content = ["user_id", "username", "pfp"],
        orders = ["!created_at", "created_at", "!username", "username"],
        searches = ["Alex1", "Bob2", "Carla3"],
        require_login = True
    )


@pytest.mark.slow
def test_followings_pagination(pagination_tests, users, create_account, follow_request):
    """Alice segue vários usuários"""

    def seed_order(follower: BaseUser, total: int, order: str = ""):
        """Cria vários usuários diferentes e faz eles seguirem o followed, em ordens diferentes"""

        usernames = [f"User{i+1}" for i in range(total)]
        create_account.cleanup()

        for u in usernames:
            followed = create_account(u)
            response = follow_request(follower, followed, cleanup=False)
            assert response.status_code == 200, response.json()

        if "!" in order:
            usernames.reverse()

        return usernames

    def seed_search(follower: BaseUser, total: int, search: str):
        """Cria vários usuários diferentes e faz o follower seguir eles, para que apareça no search depois"""

        searched_usernames = [ (search + "_" * i) for i in range(total)]
        unsearched_usernames = ["Joao", "Maria"]
        all_usernames = searched_usernames + unsearched_usernames
        create_account.cleanup()

        for u in all_usernames:
            followed = create_account(u)
            response = follow_request(follower, followed, cleanup=False)
            assert response.status_code == 200, response.json()

        searched_usernames.reverse()

        return {"match": searched_usernames, "no_match": unsearched_usernames}

    pagination_tests(
        user = users["Alice"],
        url = BASE_URL_USERS + f"/follow/followings/{users["Alice"].user_id}",
        seed_order = seed_order,
        seed_search = seed_search,
        seed_obj = "username",
        content = ["user_id", "username", "pfp"],
        orders = ["!created_at", "created_at", "!username", "username"],
        searches = ["Alex1", "Bob2", "Carla3"],
        require_login = True
    )
