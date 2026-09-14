from . import *
from .utils import *
from .test_save_list import save_list_request, assert_save


def add_game_request(user: dict, list_in: dict, game_id: int):
    return requests.post(
        url=BASE_URL + f"/game/{list_in["name"]}/{game_id}",
        cookies=user["cookies"]
    )


def rem_game_request(user: dict, list_in: dict, game_id: int):
    return requests.delete(
        url=BASE_URL + f"/game/{list_in["name"]}/{game_id}",
        cookies=user["cookies"]
    )


def view_list_games(user: dict, list_in: dict):
    response = requests.get(url=BASE_URL + f"/{list_in["name"]}", cookies=user["cookies"])
    assert response.status_code == 200
    return response.json()["games"]


def assert_game_in_list(user: dict, list_in: dict, game_id: int):
    games = view_list_games(user, list_in)
    assert any(g["game_id"] == game_id for g in games)


def assert_game_not_in_list(user: dict, list_in: dict, game_id: int):
    games = view_list_games(user, list_in)
    assert all(g["game_id"] != game_id for g in games)


# ========= Testes ===========

def test_adding_game_to_list(users, games):
    """Alice cria uma lista e adiciona um jogo a ela"""

    user = users["Alice"]
    game_id, _ = games["mario"][0]
    list_in = create_list(user)

    add_response = add_game_request(user, list_in, game_id)
    assert add_response.status_code == 200
    assert add_response.json() == SUCCESS_ADDING_MSG
    assert_game_in_list(user, list_in, game_id)

    delete_list(user, list_in)


def test_adding_and_removing_game(users, games):
    """Alice cria uma lista, adiciona um jogo e depois o remove"""

    user = users["Alice"]
    game_id, _ = games["GTA"][0]
    list_in = create_list(user)

    add_response = add_game_request(user, list_in, game_id)
    assert add_response.status_code == 200
    assert_game_in_list(user, list_in, game_id)

    rem_response = rem_game_request(user, list_in, game_id)
    assert rem_response.status_code == 200
    assert rem_response.json() == SUCCEESS_REMOVING_MSG
    assert_game_not_in_list(user, list_in, game_id)

    delete_list(user, list_in)


def test_adding_multiple_games(users, games):
    """Alice cria uma lista e adiciona vários jogos a ela"""

    user = users["Alice"]
    list_in = create_list(user)
    game_ids = [g[0] for g in games["mario"][:3]]

    for game_id in game_ids:
        add_response = add_game_request(user, list_in, game_id)
        assert add_response.status_code == 200

    for game_id in game_ids:
        assert_game_in_list(user, list_in, game_id)

    delete_list(user, list_in)


def test_adding_game_to_non_existent_list(users, games):
    """Alice tenta adicionar um jogo a uma lista que não existe"""

    user = users["Alice"]
    game_id, _ = games["roblox"][0]
    list_in = {"name": "ghost"}

    add_response = add_game_request(user, list_in, game_id)
    assert add_response.status_code == 404
    assert add_response.json() == LIST_NOT_FOUND_MSG


def test_removing_game_from_non_existent_list(users, games):
    """Alice tenta remover um jogo de uma lista que não existe"""

    user = users["Alice"]
    game_id, _ = games["roblox"][0]
    list_in = {"name": "ghost"}

    rem_response = rem_game_request(user, list_in, game_id)
    assert rem_response.status_code == 404
    assert rem_response.json() == LIST_NOT_FOUND_MSG


def test_adding_game_only_affects_own_list(users, games):
    """Alice e Bernardo criam suas próprias listas, Alice adiciona um jogo, isso não deve afetar a lista de Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]
    game_id, _ = games["mario"][0]

    list_user1 = create_list(user1)
    list_user2 = create_list(user2)

    add_response = add_game_request(user1, list_user1, game_id)
    assert add_response.status_code == 200
    assert_game_in_list(user1, list_user1, game_id)
    assert_game_not_in_list(user2, list_user2, game_id)

    delete_list(user1, list_user1)
    delete_list(user2, list_user2)


def test_cant_add_game_requests_to_list_you_dont_own(users, games):
    """Alice cria uma lista, Bernardo salva a lista, Bernardo tenta adicionar um jogo a lista de Alice"""

    user1, user2 = users["Alice"], users["Bernardo"]
    game_id, _ = games["mario"][0]

    list_user1 = create_list(user1)

    save_list_request_result = save_list_request(user2, user1, list_user1)
    assert save_list_request_result.status_code == 200
    assert_save(user2, user1, list_user1)

    add_list_result = add_game_request(user2, list_user1, game_id)
    assert add_list_result.status_code == 404
    assert add_list_result.json() == LIST_NOT_FOUND_MSG
    assert_game_not_in_list(user1, list_user1, game_id)
    