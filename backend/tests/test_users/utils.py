import pytest
import requests

BASE_URL = "http://127.0.0.1:8000/user"

SUCCESS_CREATING_STR = "Conta criada com sucesso!"
SUCCESS_FOLOWING_MSG = {"message":"Conta seguida com sucesso!"}
SUCCESS_UNFOLOWING_MSG = {"message":"Conta desseguida com sucesso!"}
SUCCESS_BLOCKING_MSG = {"message":"Conta bloqueada com sucesso!"}
SUCCESS_UNBLOCKING_MSG = {"message":"Conta desbloqueada com sucesso!"}
USER_NOT_FOUND_MSG = {"message":"Usuário não encontrado!"}
USERNAME_WRONG_LENGTH_MSG = {"message": "O username deve ter entre 4 e 24 caracteres!"}
USERNAME_IN_USE_MSG = lambda username: {"message": f'O username "{username}" já está sendo utilizado!'}
INVALID_EMAIL_MSG = {"message": "Email inválido!"}
EMAIL_IN_USE_MSG = lambda email: {"message": f'O email "{email}" já está sendo utilizado!'}
PWD_WRONG_LENGTH_MSG = {"message": "A senha deve conter entre 8 a 64 caractéres!"}
PWD_WITHOUT_NUM_MSG = {"message": "A senha deve conter pelo menos um número!"}
PWD_WITHOUT_SYMB_MSG = {"message": "A senha deve conter pelo menos um símbolo!"}
PWD_WITHOU_CAP_MSG = {"message": "A senha deve conter pelo menos uma letra minúscula e uma letra maiúscula!"}


def view_followers(user: dict):
    """Retorna por quem o user é seguido"""

    cookies = user["cookies"]
    followers = []

    host = BASE_URL[:BASE_URL.find("/user")]
    end_point = "/user/follow/followers"

    response = requests.get(host+end_point, cookies=cookies)
    assert response.status_code == 200
    response_json = response.json()
    end_point = response_json["next_page"]
    followers += response_json["content"]

    while end_point is not None:
        response = requests.get(host+end_point, cookies=cookies)
        assert response.status_code == 200
        response_json = response.json()
        end_point = response_json["next_page"]
        followers += response_json["content"]

    return followers


def view_followeds(user: dict):
    """Retorna quem o user segue"""

    cookies = user["cookies"]
    followeds = []

    url = f"{BASE_URL}/follow/followeds"

    response = requests.get(url, cookies=cookies)
    assert response.status_code == 200
    response_json = response.json()
    followeds += response_json["content"]
    url = response_json["next_page"]

    while url is not None:
        response = requests.get(url, cookies=cookies)
        assert response.status_code == 200
        response_json = response.json()
        followeds += response_json["content"]
        url = response_json["next_page"]

    return followeds


def assert_follow(atv: dict, pas: dict):
    """Garante que atv segue pas e pas é seguido por atv"""

    # atv está na lista de seguidores de pas
    followers = view_followers(pas)  
    assert any([f["username"] == atv["username"] for f in followers]), followers

    # pas está na lista de seguidos por atv
    followeds = view_followeds(atv)
    assert any([f["username"] == pas["username"] for f in followeds]), followeds


def assert_unfollow(atv: dict, pas: dict):
    """Garante que atv não segue pas e pas não é seguido por atv"""

    # atv não está na lista de seguidores de pas
    follows = view_followers(pas)
    assert all([f["username"] != atv["username"] for f in follows]), follows

    # pas não está na lista de seguidos por atv
    follows = view_followeds(atv)   
    assert all([f["username"] != pas["username"] for f in follows]), follows


def view_blocks(user: dict) -> list:
    """Retorna quem o user bloqueou"""

    cookies = user["cookies"]
    blocks = []

    response = requests.get(f"{BASE_URL}/block", cookies=cookies)
    assert response.status_code == 200
    response_json = response.json()
    blocks += response_json["content"]

    while response_json["next_page"] != None:
        response = requests.get(response_json["next_page"], cookies=cookies)
        assert response.status_code == 200
        response_json = response.json()
        blocks += response_json["content"]

    return blocks


def assert_block(atv: dict, pas: dict):
    """Garante que atv bloqueou pas"""

    # pas está na lista de bloqueados por atv
    blocks = view_blocks(atv)
    assert any([b["username"] == pas["username"] for b in blocks])


def assert_unblock(atv: dict, pas: dict):
    """Garante que atv não bloqueou pas"""

    # pas não está na lista de bloqueados por atv
    blocks = view_blocks(atv) 
    assert all([b["username"] != pas["username"] for b in blocks])
