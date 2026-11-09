from dataclasses import asdict
from dotenv import load_dotenv
import os
import pytest
import requests

load_dotenv("../.env")
os.environ["BASE_URL"] = os.getenv("BACK_URL")

from .utils import (
    BaseUser, BaseReview, BaseList, 
    Clearence, 
    BASE_URL_GAMES, BASE_URL_LISTS, BASE_URL_REVIEWS, BASE_URL_USERS, 
    NOT_LOGGED_IN_MSG, 
    create_account_by_username, delete_account
)

from . import pagination_subtests as pag_tests

def pytest_configure(config):
    """Determina os marcadores personalizados que usamos nos testes"""

    custom_markers = [
        "slow: marks tests as time consuming",
        "rawg: marks tests as rawg api dependent",
        "pagination: marks the tests that use cursor pagination",
    ]

    for cm in custom_markers:
        config.addinivalue_line("markers", cm)


def pytest_collection_modifyitems(config, items):
    """Marca os testes de paginação"""

    rawg_dependent_fixtures = ("create_review", "games")

    for item in items:
        if "pagination" in item.name:
            item.add_marker(pytest.mark.pagination)

        if any(fix in getattr(item, "fixturenames", ()) for fix in rawg_dependent_fixtures):
            item.add_marker(pytest.mark.rawg)


@pytest.fixture(scope='module')
def users():
    """Conjunto de usuários para testes"""

    created_users = {}

    def _users(username: str) -> BaseUser :
        if username not in created_users.keys():
            new_user = create_account_by_username(username)
            created_users[username] = new_user

        return created_users[username]

    yield _users

    for user in created_users.values():
        delete_account(user)


@pytest.fixture(scope='session')
def games():
    """Conjunto de games para testes"""

    def _get_games(game_name: str):
        """Pega 10 jogos relacionados a um nome na API rawg"""

        url = BASE_URL_GAMES + f"?search={game_name}" + "&detail=false&page=1&page_size=10"

        response = requests.get(url)
        assert response.status_code == 200, response.json()

        games_list = response.json()["games"]
        game_ids_list = [g["game_id"] for g in games_list]

        return game_ids_list

    games = {
        "mario": _get_games("mario"),
        "GTA": _get_games("GTA"),
        "roblox": _get_games("roblox"),
    }

    return games


@pytest.fixture
def follow_request():
    """Faz o request para seguir um usuário
    cleanup = True significa que vai apagar do DB depois"""

    responses = []

    # Tenta inserir o block no DB
    def _follow(atv: BaseUser, pas: BaseUser, cleanup: bool = True):
        target, cookies = pas.user_id, atv.cookies
        post_resp = requests.post(BASE_URL_USERS + f"/follow/{target}", cookies=cookies)
        if cleanup:
            assert post_resp.status_code == 200, post_resp.json()
            responses.append({"target": target, "cookies": cookies})
        return post_resp

    yield _follow

    # Faz o cleanup
    for r in responses:
        target, cookies = r["target"], r["cookies"]
        del_resp = requests.delete(BASE_URL_USERS + f"/follow/{target}", cookies=cookies)
        assert del_resp.status_code == 200, del_resp.json()


@pytest.fixture
def unfollow_request():
    """Faz o request para desseguir um usuário"""

    # Tenta deletar o block do DB
    def _unfollow_request(atv: BaseUser, pas: BaseUser):
        target, cookies = pas.user_id, atv.cookies
        return requests.delete(BASE_URL_USERS + f"/follow/{target}", cookies=cookies)

    return _unfollow_request


@pytest.fixture
def block_request():
    """Faz o request para bloquear um usuário. 
    cleanup = True significa que vai apagar do DB depois"""

    blockeds = []

    def _block_request(atv: BaseUser, pas: BaseUser, cleanup: bool = True):
        """Tenta inserir o block no DB"""
        target, cookies = pas.user_id, atv.cookies
        response = requests.post(BASE_URL_USERS + f"/block/{target}", cookies=cookies)

        if cleanup:
            assert response.status_code == 200, response.json()
            blockeds.append({"target": target, "cookies": cookies})

        return response

    def _cleanup():
        """Desfaz os bloqueios criados até agora"""
        while len(blockeds) > 0:
            b = blockeds.pop()
            target, cookies = b["target"], b["cookies"]
            response = requests.delete(BASE_URL_USERS + f"/block/{target}", cookies=cookies)
            assert response.status_code == 200


    yield _block_request

    _cleanup()


@pytest.fixture
def unblock_request():
    """Faz o request para desbloquear um usuário"""

    # Tenta deletar o block do DB
    def _unblock_request(atv: BaseUser, pas: BaseUser):
        target, cookies = pas.user_id, atv.cookies
        return requests.delete(BASE_URL_USERS + f"/block/{target}", cookies=cookies)

    return _unblock_request


@pytest.fixture
def create_account():
    """Cria uma conta no DB
    cleanup = True significa que vai apagar do DB depois"""

    accounts = []

    def _create_account(username: str, cleanup: bool = True):
        """Cria uma conta a partir do username providenciado"""

        account = create_account_by_username(username)
        if cleanup:
            accounts.append(account)
        return account

    def _cleanup():
        """Apaga todas as contas criadas até agora"""

        while len(accounts) > 0:
            delete_account(accounts.pop())

    _create_account.cleanup = _cleanup

    yield _create_account

    _cleanup()


@pytest.fixture()
def create_review(games):
    """Insere uma review no DB.
    Se o cleanup for True, depois a remove do DB"""

    reviews = []

    def _create_review(user: BaseUser, game_id: int = None, privacy: int = Clearence.ANY, cleanup: bool = True, liked: bool = True, completed: bool = True):
        """ Insere a review no DB """
        review = BaseReview(
            game_id = game_id if game_id is not None else games["mario"][0],
            rating_num = 3.5,
            rating_text = "Muito bom, recomendo!",
            liked = liked,
            privacy = privacy,
            time_played = 15,
            completed = completed,
        )

        create_response = requests.post(url=BASE_URL_REVIEWS, json=asdict(review), cookies=user.cookies)

        assert create_response.status_code == 200, create_response.json()
        assert "review_id" in create_response.json().keys()
        review_id = create_response.json()["review_id"]
        review.review_id = review_id

        if cleanup:
            reviews.append({"cookies": user.cookies, "review_id": review_id})

        return review


    def _cleanup():
        """Apaga as reviews criadas até agora"""

        while len(reviews) > 0:
            review = reviews.pop()
            delete_response = requests.delete(url=BASE_URL_REVIEWS + f"/{review["review_id"]}", cookies=review["cookies"])
            assert delete_response.status_code == 200
            assert delete_response.json() == {"message": "Review deletada com sucesso!"}

    _create_review.cleanup = _cleanup

    yield _create_review

    _cleanup()


@pytest.fixture
def edit_review_request():
    """Faz o request para editar uma review de usuário"""

    # Tenta editar a review no DB
    def _edit_review_request(user: BaseUser, review: dict):
        review_copy = review.copy()
        id = review_copy.pop("review_id")
        return requests.put(f"{BASE_URL_REVIEWS}/{id}", cookies=user.cookies, json=review_copy)

        
    return _edit_review_request


@pytest.fixture(params=[(7, 4), (9, 4), (8, 4), (3, 4), (401, 401)])
def pagination_tests(subtests, request):
    """Testes completos para rotas paginadas"""

    def _pagination_tests(user: BaseUser, url: str, seed, require_login: bool):

        if all(rp == 401 for rp in request.param):

            pag_tests.queries_tests(subtests, user, url)
        
            if require_login:
                response = requests.get(url)
                assert response.status_code == 401, response.json()
                assert response.json() == NOT_LOGGED_IN_MSG

        else:
            pag_tests.content_tests(user, url, seed, *request.param)
            pag_tests.order_tests(subtests, user, url, seed, *request.param)
            pag_tests.search_tests(subtests, user, url, seed, *request.param)

    return _pagination_tests