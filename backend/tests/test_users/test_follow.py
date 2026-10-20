from .utils import *


def test_follow_returns_200(users, follow_request):
    """Alice segue Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow_request(user1, user2)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_FOLLOWING_MSG
    assert_follow(user1, user2)


def test_unfollow_returns_200(users, follow_request, unfollow_request):
    """Alice segue e dessegue Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    follow_resp = follow_request(user1, user2, False)
    assert follow_resp.status_code == 200, follow_resp.json()

    response = unfollow_request(user1, user2)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_UNFOLLOWING_MSG
    assert_unfollow(user1, user2)


def test_follow_twice_returns_200_twice(users, follow_request):
    """Alice segue Bernardo 2 vezes"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow_request(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)

    response = follow_request(user1, user2)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)


def test_unfollow_someone_not_followed_returns_200(users, unfollow_request):
    """Alice dessegue Bernardo sem antes segui-lo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = unfollow_request(user1, user2)
    assert response.status_code == 200, response.json()
    assert_unfollow(user1, user2)


def test_follow_someone_that_doenst_exist_returns_404(users, follow_request):
    """Alice segue inexistente"""

    user1, inexistent = users["Alice"], BaseUser(user_id = "inexistente")

    response = follow_request(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_unfollow_someone_that_doenst_exist_returns_404(users, unfollow_request):
    """Alice dessegue inexistente"""

    user1, inexistent = users["Alice"], BaseUser(user_id = "inexistente")
    
    response = unfollow_request(user1, inexistent)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_following_yourself_returns_403(users, follow_request):
    """Alice segue Alice"""

    user = users["Alice"]

    response = follow_request(user, user, False)
    assert response.status_code == 403, response.json()
    assert response.json() == CANT_FOLLOW_YOURSELF_MSG
    assert_unfollow(user, user)



