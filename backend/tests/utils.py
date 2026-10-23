import pytest, requests, copy
from enum import IntEnum
from requests.cookies import RequestsCookieJar
from dataclasses import dataclass, replace, asdict

BASE_URL = "http://127.0.0.1:8000"
BASE_URL_USERS = BASE_URL + "/users"
BASE_URL_LISTS = BASE_URL + "/lists"
BASE_URL_REVIEWS = BASE_URL + "/reviews"
BASE_URL_GAMES = BASE_URL + "/games"

class Clearence(IntEnum):
    """Possíveis nívels de permissão para visibilidade de uma lista/review"""
    ANY = 0
    FOLLOWED = 10
    OWNER = 40


@dataclass
class BaseUser:
    user_id: str | None = None
    username: str | None = "user1"
    pwd: str | None = "UserUser1!"
    email: str | None = "user1@gmail.com"
    bio: str | None = None
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


def view_followers(user: BaseUser):
    """Retorna por quem o user é seguido"""

    followers = []
    url = BASE_URL_USERS + f"/follow/followers/{user.user_id}?page_size=40"

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

    url = BASE_URL_USERS + f"/follow/following/{user.user_id}?page_size=50"

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

    url = BASE_URL_USERS + "/block?page_size=50"

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


