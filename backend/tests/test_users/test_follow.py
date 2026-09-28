from .utils import *

# users é um fixture definido em tests/conftest.py
# follow é um fixture definido em tests/conftest.py
# unfollow é um fixture definido em tests/conftest.py

def test_follow_returns_200(users, follow):
    """Alice segue Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_FOLOWING_MSG
    assert_follow(user1, user2)


def test_unfollow_returns_200(users, unfollow):
    """Alice dessegue Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = unfollow(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_UNFOLOWING_MSG
    assert_unfollow(user1, user2)


def test_follow_twice_returns_200_twice(users, follow):
    """Alice segue Bernardo 2 vezes"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)

    response = follow(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)


def test_unfollow_someone_not_followed_returns_200(users, unfollow):
    """Alice dessegue Bernardo sem antes segui-lo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = unfollow(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_unfollow(user1, user2)


def test_follow_someone_that_doenst_exist_returns_404(users, follow):
    """Alice segue inexistente"""

    user1, inexistent = users["Alice"], {"username": "inexistente"}

    response = follow(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_unfollow_someone_that_doenst_exist_returns_404(users, unfollow):
    """Alice dessegue inexistente"""

    user1, inexistent = users["Alice"], {"username": "inexistente"}
    
    response = unfollow(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_following_yourself_returns_403(users, follow):
    """Alice segue Alice"""

    user1, user2 = users["Alice"], users["Alice"]

    response = follow(user1, user2, False)
    assert response.status_code == 403, response.json()
    assert response.json() == {"message":"O usuário não pode seguir a si mesmo!"}
    assert_unfollow(user1, user2)
