from dataclasses import dataclass
from enum import IntEnum
import os
import requests
from requests.cookies import RequestsCookieJar


BASE_URL = os.environ["BASE_URL"]
BASE_URL_USERS = os.environ["BASE_URL"] + "/users"
BASE_URL_LISTS = os.environ["BASE_URL"] + "/lists"
BASE_URL_REVIEWS = os.environ["BASE_URL"] + "/reviews"
BASE_URL_GAMES = os.environ["BASE_URL"] + "/games"

NOT_LOGGED_IN_MSG = {"message" : "É necessário fazer login para esta ação!"}
USER_NOT_FOUND_MSG = {"message":"Usuário não encontrado!"}
REVIEW_NOT_FOUND_MSG = {"message": "Review não encontrada!"}
GAME_NOT_FOUND_MSG = {"message": "Game não encontrado!"}
LIST_NOT_FOUND_MSG = {"message": "Lista não encontrada!"}


class Clearence(IntEnum):
    """Possíveis nívels de permissão para visibilidade de uma lista/review"""
    ANY = 0
    FOLLOWED = 20
    OWNER = 40


@dataclass
class BaseUser:
    user_id: str | None = None
    username: str | None = "user1"
    pwd: str | None = "UserUser1!"
    email: str | None = "user1@gmail.com"
    bio: str | None = None
    pfp: str | None = None
    banner: str | None = None
    cookies: RequestsCookieJar | None = None


@dataclass
class BaseList:
    list_id: str  | None = None
    name: str | None = "Wishlist"
    privacy: int | None = Clearence.ANY
    description: str | None = "Jogos que quero jogar"
    first_games: tuple = ()


@dataclass
class BaseReview:
    review_id: str | None = None
    game_id: int = -1,
    rating_num: float = 3.5,
    rating_text: str = "Muito bom, recomendo!",
    privacy: int = Clearence.ANY,
    time_played: int = 15
    liked: bool = True,
    completed: bool = True


def create_account_by_username(username: str):
    """Insere uma conta no DB pelo username"""

    payload = {"username": username, "password": f"{username}{username}1!", "email": f"{username}@gmail.com"}

    session = requests.Session()
    response = session.post(BASE_URL_USERS, json=payload)

    for c in session.cookies:
        c.secure = False

    response_json = response.json()

    assert response.status_code == 200, response_json
    assert "message" in response_json.keys()
    assert response_json["message"] == "Conta criada com sucesso!"
    assert "user_id" in response_json.keys()

    return BaseUser(
        user_id = response_json["user_id"],
        username=payload["username"],
        pwd=payload["password"],
        email=payload["email"],
        cookies=session.cookies
    )


def delete_account(user: BaseUser):
    """Deleta uma conta do DB"""

    response = requests.delete(BASE_URL_USERS, cookies=user.cookies)

    assert response.status_code == 200
    assert response.json() == {"message":"Conta deletada com sucesso!"}


def view_followers(user: BaseUser):
    """Retorna por quem o user é seguido"""

    followers = []
    url = BASE_URL_USERS + f"/follow/followers/{user.user_id}"

    response = requests.get(url, cookies=user.cookies)
    assert response.status_code == 200, response.json()
    followers += response.json()["content"]
    url = response.json()["next_url"]

    while url is not None:
        response = requests.get(url, cookies=user.cookies)
        assert response.status_code == 200, response.json()
        followers += response.json()["content"]
        url = response.json()["next_url"]

    return followers


def view_followeds(user: BaseUser):
    """Retorna quem o user segue"""

    followeds = []

    url = BASE_URL_USERS + f"/follow/followings/{user.user_id}"

    response = requests.get(url, cookies=user.cookies)
    assert response.status_code == 200, response.json()
    followeds += response.json()["content"]
    url = response.json()["next_url"]

    while url is not None:
        response = requests.get(url, cookies=user.cookies)
        assert response.status_code == 200, response.json()
        followeds += response.json()["content"]
        url = response.json()["next_url"]

    return followeds


def assert_follow(atv: BaseUser, pas: BaseUser):
    """Garante que atv segue pas e pas é seguido por atv"""

    # atv está na lista de seguidores de pas
    followers = view_followers(pas)  
    assert any([f["username"] == atv.username for f in followers]), followers

    # pas está na lista de seguidos por atv
    followeds = view_followeds(atv)
    assert any([f["username"] == pas.username for f in followeds]), followeds


def assert_unfollow(atv: BaseUser, pas: BaseUser):
    """Garante que atv não segue pas e pas não é seguido por atv"""

    # atv não está na lista de seguidores de pas
    followers = view_followers(pas)
    assert all([f["username"] != atv.username for f in followers]), followers

    # pas não está na lista de seguidos por atv
    followeds = view_followeds(atv)   
    assert all([f["username"] != pas.username for f in followeds]), followeds


def view_blocks(user: BaseUser):
    """Retorna quem o user bloqueou"""

    blocks = []

    url = BASE_URL_USERS + "/block"

    response = requests.get(url, cookies=user.cookies)
    assert response.status_code == 200, response.json()
    blocks += response.json()["content"]
    url = response.json()["next_url"]

    while url is not None:
        response = requests.get(url, cookies=user.cookies)
        assert response.status_code == 200, response.json()
        blocks += response.json()["content"]
        url = response.json()["next_url"]

    return blocks


def assert_block(atv: BaseUser, pas: BaseUser):
    """Garante que atv bloqueou pas"""

    # pas está na lista de bloqueados por atv
    blocks = view_blocks(atv)
    assert any([b["username"] == pas.username for b in blocks])


def assert_unblock(atv: BaseUser, pas: BaseUser):
    """Garante que atv não bloqueou pas"""

    # pas não está na lista de bloqueados por atv
    blocks = view_blocks(atv) 
    assert all([b["username"] != pas.username for b in blocks])


