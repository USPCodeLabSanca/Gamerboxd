from dataclasses import asdict
import pytest
import random
import requests

from ..utils import BaseUser, BaseList, Clearence, BASE_URL_LISTS, NOT_LOGGED_IN_MSG
from .utils import (
    SUCCESS_CREATING_MSG, 
    LIST_NAME_TAKEN_MSG, LIST_NAME_TOO_BIG_MSG, LIST_NAME_BLANK_MSG, 
    LIST_DESC_TOO_BIG_MSG, LIST_DESC_BLANK_MSG,
    assert_game_in_list, assert_game_not_in_list
)


def base_list(num:int, **overrides):
    """Json padrão de uma lista"""

    list_in = {"name": f"list_{num}", "privacy": Clearence.OWNER, "first_games": []}
    list_in.update(overrides)
    return list_in


new_lists = [
    # Testes funcionais
    (base_list(1, description="list1", privacy=Clearence.ANY), 200,  SUCCESS_CREATING_MSG),
    (base_list(2, description="list2"), 200,  SUCCESS_CREATING_MSG),
    (base_list(3, privacy=Clearence.FOLLOWED), 200,  SUCCESS_CREATING_MSG),
    (base_list(4), 200, SUCCESS_CREATING_MSG),
    (base_list(5, name="a"), 200, SUCCESS_CREATING_MSG),
    (base_list(6, description="a"), 200, SUCCESS_CREATING_MSG),

    # Testes de erros do usuário na hora de criar conta
    (base_list(1), 409, LIST_NAME_TAKEN_MSG("list_1")),
    (base_list(8, name="list6"*10), 400, LIST_NAME_TOO_BIG_MSG),
    (base_list(9, name="  "), 400, LIST_NAME_BLANK_MSG),
    (base_list(10, description="list8"*61), 400,  LIST_DESC_TOO_BIG_MSG),
    (base_list(11, description="  "), 400,  LIST_DESC_BLANK_MSG),

    # Testes de schema inválido/mal formatado
    (base_list(12, name=8), 422, None),
    (base_list(13, name=None), 422, None),
    ({"list_name": "list_10"}, 422, None),
    (base_list(14, description=11), 422, None),
    (base_list(15, privacy="private"), 422, None),
    (base_list(16, privacy=None), 422, None),  
    (base_list(17, privacy=10), 422, None)
]


@pytest.mark.parametrize("list_in,expected_status,expected_body", new_lists)
def test_new_lists(users, list_in, expected_status, expected_body):

    user = users("Alice")
    cookies = user.cookies

    # Força a duplicidade para testes de conflito
    if expected_status == 409:
        list1 = base_list(1)
        response_duplicate = requests.post(url=BASE_URL_LISTS, json=list1, cookies=cookies)
        assert response_duplicate.status_code == 200
        duplicate_list_id = response_duplicate.json()["list_id"]

    response = requests.post(url=BASE_URL_LISTS, json=list_in, cookies=cookies)
    assert response.status_code == expected_status, response.json()

    if expected_body is not None:
        assert expected_body.keys() == response.json().keys()
        assert expected_body["message"] == response.json()["message"]

        list_id = response.json()["list_id"] if expected_status == 200 else None

    if response.status_code == 200:
        response_delete = requests.delete(url=BASE_URL_LISTS + f"/{list_id}", cookies=cookies)
        assert response_delete.status_code == 200

    if expected_status == 409:
        response_delete_duplicate = requests.delete(url=BASE_URL_LISTS + f"/{duplicate_list_id}", cookies=cookies)
        assert response_delete_duplicate.status_code == 200


def test_creating_list_with_games_returns_200(users, games):
    """Alice cria uma lista já enviando os primeiros games dela"""

    user = users("Alice")
    games_list = games["mario"]
    list_in = base_list(1, first_games=games_list)

    response = requests.post(url=BASE_URL_LISTS, json=list_in, cookies=user.cookies)
    assert response.status_code == 200, response.json()
    assert "list_id" in response.json().keys()
    assert len(response.json()["not_included"]) == 0, response.json()["not_included"]

    list_with_games = BaseList(list_id=response.json()["list_id"])

    for g in games_list:
        assert_game_in_list(user, list_with_games, g)

    response = requests.delete(url=BASE_URL_LISTS+f"/{list_with_games.list_id}", cookies=user.cookies)
    assert response.status_code == 200, response.json()


def test_creating_list_with_invalid_games_returns_invalid_games_and_200(users, games):
    """Alice cria uma lista, mas um dos game-ids para inserir na lista não são válidos"""

    user = users("Alice")
    invalid_games = [-1, -2]
    games_list = games["mario"] + invalid_games
    list_in = base_list(1, first_games=games_list)

    response = requests.post(url=BASE_URL_LISTS, json=list_in, cookies=user.cookies)
    assert response.status_code == 200, response.json()
    assert "list_id" in response.json().keys()
    assert len(response.json()["not_included"]) == len(invalid_games), response.json()["not_included"]

    list_with_games = BaseList(list_id=response.json()["list_id"])

    for g in games_list:

        if g not in invalid_games:
            assert_game_in_list(user, list_with_games, g)

        else:
            assert_game_not_in_list(user, list_with_games, g)

    response = requests.delete(url=BASE_URL_LISTS+f"/{list_with_games.list_id}", cookies=user.cookies)
    assert response.status_code == 200, response.json()


def test_creating_list_while_not_logged_in_returns_401():
    """Um usuário tenta criar uma lista sem enviar os cookies"""

    list_in = base_list(100)
    response = requests.post(url=BASE_URL_LISTS, json=list_in)
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG


def test_list_creation_pagination(pagination_tests, users, create_list, edit_list_request):
    """Alice cria várias listas"""

    def seed(creator: BaseUser, total: int, order: str = "", search: str = None):
        """Cria as várias listas"""

        list_names = [f"List{i+1}" for i in range(total-2)] if search is None else [(search + "_" * i) for i in range(total)]

        new_lists = [create_list(creator, list_name = l) for l in list_names]

        if ("updated" in order) or (len(order) == 0):
            random.shuffle(new_lists)
            for nl in new_lists:
                nl.privacy = Clearence.FOLLOWED
                response = edit_list_request(creator, asdict(nl))
                assert response.status_code == 200, response.json()

        shuffeled_list_names = [nl.name for nl in new_lists]
            
        if ("!" in order) or (len(order) == 0):
            shuffeled_list_names.reverse()

        return shuffeled_list_names

    seed.cleanup = create_list.cleanup
    seed.expected_content = ["list_id", "name", "creator", "saves_count", "cover_picture", "rel", "privacy"]
    seed.valid_orders = ["created_at", "name", "updated_at"]
    seed.searches = ["Playstation", "Minecraft", "Esporte"]
    seed.return_obj = "name"
    seed.ignore = ["Jogos Completados", "Jogos Favoritos"]
    
    pagination_tests(
        user = users("Alice"),
        url = BASE_URL_LISTS + f"/created/{users("Alice").user_id}",
        seed = seed,
        require_login = False
    )
