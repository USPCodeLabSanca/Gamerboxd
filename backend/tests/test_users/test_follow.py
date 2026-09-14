from . import *

def follow(atv: dict, pas: dict):
    """Roda o follow no backend"""

    target, cookies = pas["username"], atv["cookies"]
    return requests.post(f"{BASE_URL}/follow/{target}", cookies=cookies)

def unfollow(atv: dict, pas: dict):
    """Roda o unfollow no backend"""

    target, cookies = pas["username"], atv["cookies"]
    return requests.delete(f"{BASE_URL}/follow/{target}", cookies=cookies)

def view_follow(atv: dict):
    cookies = atv["cookies"]
    return requests.get(f"{BASE_URL}/follow", cookies=cookies)

def assert_follow(atv: dict, pas: dict):
    """Garante que atv segue pas e pas é seguido por atv"""

    response = view_follow(atv)  
    assert any([f["username"] == pas["username"] for f in response.json()["followings"]])

    response = view_follow(pas)
    assert any([f["username"] == atv["username"] for f in response.json()["followers"]])

def assert_unfollow(atv: dict, pas: dict):
    """Garante que atv não segue pas e pas não é seguido por atv"""
    
    response = view_follow(atv)   
    assert all([f["username"] != pas["username"] for f in response.json()["followings"]])

    response = view_follow(pas)
    assert all([f["username"] != atv["username"] for f in response.json()["followers"]])


# ========= Testes ===========

def test_follow(users):
    """Alice segue e depois dessegue Bernardo"""

    atv, pas = users["Alice"], users["Bernardo"]

    response = follow(atv, pas)
    assert response.status_code == 200
    assert response.json() == SUCCESS_FOLOWING_MSG
    assert_follow(atv, pas)

    response = unfollow(atv, pas)
    assert response.status_code == 200
    assert response.json() == SUCCESS_UNFOLOWING_MSG
    assert_unfollow(atv, pas)


def test_follow_twice(users):
    """Bernardo segue Caua 2 vezes"""

    atv, pas = users["Bernardo"], users["Caua"]

    response = follow(atv, pas)
    assert response.status_code == 200
    assert response.json() == SUCCESS_FOLOWING_MSG
    assert_follow(atv, pas)

    response = follow(atv, pas)
    assert response.status_code == 200
    assert response.json() == SUCCESS_FOLOWING_MSG
    assert_follow(atv, pas)


def test_unfollow_someone_not_followed(users):
    """Caua dessegue Daniela"""

    atv, pas = users["Caua"], users["Daniela"]

    response = unfollow(atv, pas)
    assert response.status_code == 200
    assert response.json() == SUCCESS_UNFOLOWING_MSG
    assert_unfollow(atv, pas)


def test_follow_someone_that_doenst_exist(users):
    """Daniela segue e dessegue inexistente"""

    atv, inexistent = users["Daniela"], {"username": "inexistente"}

    response = follow(atv, inexistent)
    assert response.status_code == 404
    assert response.json() == USER_NOT_FOUND_MSG

    response = unfollow(atv, inexistent)
    assert response.status_code == 404
    assert response.json() == USER_NOT_FOUND_MSG


def test_follow_yourself(users):
    """Eduarda segue Eduarda"""

    atv, pas = users["Eduarda"], users["Eduarda"]

    response = follow(atv, pas)
    assert response.status_code == 403
    assert response.json() == {"message":"O usuário não pode seguir a si mesmo!"}
    assert_unfollow(atv, pas)



