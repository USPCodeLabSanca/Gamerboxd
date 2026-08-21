from . import BASE_URL, pytest, requests

def follow(atv: dict, pas: dict):
    target, cookies = pas["username"], atv["cookies"]
    return requests.post(f"{BASE_URL}/follow/{target}", cookies=cookies)

def unfollow(atv: dict, pas: dict):
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


def test_follow(users):
    """Alice segue e depois dessegue Bernardo"""

    response = follow(users["Alice"], users["Bernardo"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta seguida com sucesso!"}
    assert_follow(users["Alice"], users["Bernardo"])

    response = unfollow(users["Alice"], users["Bernardo"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta desseguida com sucesso!"}
    assert_unfollow(users["Alice"], users["Bernardo"])


def test_follow_twice(users):
    """Bernardo segue Caua 2 vezes"""

    response = follow(users["Bernardo"], users["Caua"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta seguida com sucesso!"}
    assert_follow(users["Bernardo"], users["Caua"])

    response = follow(users["Bernardo"], users["Caua"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta seguida com sucesso!"}
    assert_follow(users["Bernardo"], users["Caua"])


def test_unfollow_someone_not_followed(users):
    """Caua dessegue Daniela"""

    response = unfollow(users["Caua"], users["Daniela"])
    assert response.status_code == 200
    assert response.json() == {"message":"Conta desseguida com sucesso!"}
    assert_unfollow(users["Caua"], users["Daniela"])


def test_follow_someone_that_doenst_exist(users):
    """Daniela segue e dessegue inexistente"""

    inexistent = {"username": "inexistente"}

    response = follow(users["Daniela"], inexistent)
    assert response.status_code == 404
    assert response.json() == {"message":"Usuário não encontrado!"}

    response = unfollow(users["Daniela"], inexistent)
    assert response.status_code == 404
    assert response.json() == {"message":"Usuário não encontrado!"}


def test_follow_yourself(users):
    """Eduarda segue Eduarda"""

    response = follow(users["Eduarda"], users["Eduarda"])
    assert response.status_code == 403
    assert response.json() == {"message":"O usuário não pode seguir a si mesmo!"}
    assert_unfollow(users["Eduarda"], users["Eduarda"])



