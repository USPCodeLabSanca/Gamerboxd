from dotenv import load_dotenv
from pathlib import Path
import os
import math

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
os.environ["BASE_URL"] = os.getenv("BACK_URL")

from .utils import *

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )

    config.addinivalue_line(
        "markers", "rawg: marks tests as rawg api dependent (deselect with '-m \"not rawg\"')"
    )

@pytest.fixture(scope='module')
def users():
    """Conjunto de usuários para testes"""

    users = {
        "Alice": create_account_by_username("Alice"),
        "Bernardo": create_account_by_username("Bernardo"),
        "Caua": create_account_by_username("Caua"),
        "Daniela" :create_account_by_username("Daniela"),
    }

    yield users

    for user in users.values():
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

    responses = []

    # Tenta inserir o block no DB
    def _block_request(atv: BaseUser, pas: BaseUser, cleanup: bool = True):
        target, cookies = pas.user_id, atv.cookies
        block_resp = requests.post(BASE_URL_USERS + f"/block/{target}", cookies=cookies)

        if cleanup:
            assert block_resp.status_code == 200, block_resp.json()
            responses.append({"target": target, "cookies": cookies})

        return block_resp

    yield _block_request

    # Faz o cleanup
    for r in responses:
        target, cookies = r["target"], r["cookies"]
        del_resp = requests.delete(BASE_URL_USERS + f"/block/{target}", cookies=cookies)
        assert del_resp.status_code == 200


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
def create_review():
    """Insere uma review no DB
    se o cleanup for True, depois a remove do DB"""

    responses = []

    # Insere a review no DB
    def _create_review(user: BaseUser, game_id: int, privacy: int = Clearence.ANY, cleanup: bool = True, liked: bool = True, completed: bool = True):
        review = BaseReview(
            game_id = game_id,
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
            responses.append({"cookies": user.cookies, "review_id": review_id})

        return review

    yield _create_review

    # Remove a review do DB
    for r in responses:
        del_resp = requests.delete(url=BASE_URL_REVIEWS + f"/{r["review_id"]}", cookies=r["cookies"])
        assert del_resp.status_code == 200
        assert del_resp.json() == {"message": "Review deletada com sucesso!"}


@pytest.fixture
def edit_review_request():
    """Faz o request para editar uma review de usuário"""

    # Tenta editar a review no DB
    def _edit_review_request(user: BaseUser, review: BaseReview):
        review_copy = asdict(copy.copy(review))
        id = review_copy.pop("review_id")
        return requests.put(f"{BASE_URL_REVIEWS}/{id}", cookies=user.cookies, json=review_copy)

        
    return _edit_review_request


@pytest.fixture
def queries_tests():
    """Testa que a API está validando os query parameters enviados antes de passar para a rota"""

    def _queries_tests(user: BaseUser, url: str, total: int, page_size: int):

        # Testes para orders invalidos
        if total < 0:
            url += f"?page_size={page_size}&order=AAAAAAAA"
            response = requests.get(url, cookies = user.cookies)
            assert response.status_code == 422, response.json()
            assert response.json() == {"message": "Método de ordenação inválido!"}

        # Testes para page_sizes inválidos
        elif page_size < 0:  
            url += f"?page_size={page_size}"
            response = requests.get(url, cookies = user.cookies)
            assert response.status_code == 422, response.json()
            assert response.json() == {"message": "O tamanho da página tem que estar entre 1 e 50!"}

        elif page_size > 50:
            url += f"?page_size={page_size}"
            response = requests.get(url, cookies = user.cookies)
            assert response.status_code == 422, response.json()
            assert response.json() == {"message": "O tamanho da página tem que estar entre 1 e 50!"}

    return _queries_tests

@pytest.fixture
def content_tests():
    """Testa que a API está retornando o tipo de registro esperado e também a quantidade de resgitros esperados"""

    def _content_tests(user: BaseUser, url: str, seed, total: int, page_size: int, content: list):

        seed(user, total)
        
        current = url + f"?page_size={page_size}"
        num_pages = math.ceil(total/page_size)
        pages_seen = 0

        while (pages_seen < num_pages):
            response = requests.get(current, cookies = user.cookies)
            assert response.status_code == 200, response.json()
            assert response.json()["total"] == total
            assert response.json()["page_len"] <= page_size
            assert response.json()["current_url"] == current

            for c in response.json()["content"]:
                assert sorted(c.keys()) == sorted(content)

            current = response.json()["next_url"]
            pages_seen += 1

        assert current is None

    return _content_tests


@pytest.fixture
def order_tests(subtests):
    """Testa que a ordenação dos registros adicionados estão como esperado nas páginas de resposta da API"""

    def _order_tests(user: BaseUser, url: str, seed, seed_obj: str, total: int, page_size: int, orders: list):

        for order in orders:
            seen_objects = []
            with subtests.test(msg=f"Testing order {order}",):

                results = seed(user, total, order=order)
                
                current = url + f"?page_size={page_size}"
                if len(order) != 0:
                    current += f"&order={order}"
                num_pages = math.ceil(total/page_size)
                pages_seen = 0

                while (pages_seen < num_pages):
                    response = requests.get(current, cookies = user.cookies)
                    assert response.status_code == 200, response.json()
                    assert response.json()["total"] == total
                    assert response.json()["page_len"] <= page_size
                    assert response.json()["current_url"] == current

                    for c in response.json()["content"]:
                        assert c[seed_obj] not in seen_objects, seen_objects
                        seen_objects.append(c[seed_obj])

                    current = response.json()["next_url"]
                    pages_seen += 1

                assert current is None
                assert seen_objects == results

    return _order_tests


@pytest.fixture
def search_tests(subtests):
    """Testa que buscar por registros adicionados retorna como esperado nas páginas de resposta da API"""

    def search_tests(user: BaseUser, url: str, seed, seed_obj: str, total: int, page_size: int, searches: list[str]):

        for search in searches:
            seen_objects = []
            with subtests.test(msg=f"Testing search {search}",):

                results = seed(user, total, search=search)
                
                current = url + f"?page_size={page_size}&search={search}"
                num_pages = math.ceil(total/page_size)
                pages_seen = 0

                while (pages_seen < num_pages):
                    response = requests.get(current, cookies = user.cookies)
                    assert response.status_code == 200, response.json()
                    assert response.json()["total"] == total
                    assert response.json()["page_len"] <= page_size
                    assert response.json()["current_url"] == current

                    for c in response.json()["content"]:
                        assert c[seed_obj] not in seen_objects, seen_objects
                        assert c[seed_obj] not in results["no_match"]
                        seen_objects.append(c[seed_obj])

                    current = response.json()["next_url"]
                    pages_seen += 1

                assert current is None
                assert seen_objects == results["match"], results

    return search_tests


@pytest.fixture(params=[(4, 7), (4, 9), (4, 8), (4, 3), (4, -1), (-1, 10), (401, 401)])
def pagination_tests(request, content_tests, order_tests, search_tests, queries_tests):
    """Testes completos para rotas paginadas"""

    def _pagination_tests(user: BaseUser, url: str, seed_order, seed_search, seed_obj: str, content: list, orders: list, searches: list, require_login: bool):

        if (request.param[1] == 401) and (request.param[0] == 401) and (require_login):
            response = requests.get(url)
            assert response.status_code == 401, response.json()
            assert response.json() == {"message" : "É necessário fazer login para esta ação!"}

        if (request.param[1] not in range(0, 50)) or (request.param[0] < 0):
            queries_tests(
                user = user,
                url = url,
                total = request.param[1],
                page_size = request.param[0]
            )

        else:

            content_tests(
                user = user, 
                url = url,
                seed = seed_order,
                total = request.param[1],
                page_size = request.param[0],
                content = content
            )

            order_tests(
                user = user, 
                url = url,
                seed = seed_order,
                seed_obj = seed_obj,
                total = request.param[1],
                page_size = request.param[0],
                orders = orders
            )

            search_tests(
                user = user, 
                url = url,
                seed = seed_search,
                seed_obj = seed_obj,
                total = request.param[1],
                page_size = request.param[0],
                searches = searches
            )

    return _pagination_tests