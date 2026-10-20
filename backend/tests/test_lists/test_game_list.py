from .utils import *


def test_adding_game_to_list_returns_200(users, games, create_list, add_game_request):
    """Alice cria uma lista e adiciona um jogo a ela"""

    user = users["Alice"]
    game_id = games["mario"][0]
    list_in = create_list(user)

    add_response = add_game_request(user, list_in, game_id)
    assert add_response.status_code == 200, add_response.json()
    assert add_response.json() == SUCCESS_ADDING_MSG
    assert_game_in_list(user, list_in, game_id)


def test_adding_and_removing_game_returns_200(users, games, create_list, add_game_request, rem_game_request):
    """Alice cria uma lista, adiciona um jogo e depois o remove"""

    user = users["Alice"]
    game_id = games["GTA"][0]
    list_in = create_list(user)

    add_response = add_game_request(user, list_in, game_id)
    assert add_response.status_code == 200, add_response.json()
    assert_game_in_list(user, list_in, game_id)

    rem_response = rem_game_request(user, list_in, game_id)
    assert rem_response.status_code == 200, rem_response.json()
    assert rem_response.json() == SUCCEESS_REMOVING_MSG
    assert_game_not_in_list(user, list_in, game_id)


def test_adding_multiple_games_all_return_200(users, games, create_list, add_game_request):
    """Alice cria uma lista e adiciona vários jogos a ela"""

    user = users["Alice"]
    list_in = create_list(user)
    game_ids = games["mario"][:3]

    for game_id in game_ids:
        add_response = add_game_request(user, list_in, game_id)
        assert add_response.status_code == 200, add_response.json()
        assert_game_in_list(user, list_in, game_id)


def test_adding_game_to_non_existent_list_returns_404(users, games, add_game_request):
    """Alice tenta adicionar um jogo a uma lista que não existe"""

    user = users["Alice"]
    game_id = games["roblox"][0]
    list_in = BaseList(list_id = "inexistent")

    add_response = add_game_request(user, list_in, game_id)
    assert add_response.status_code == 404, add_response.json()
    assert add_response.json() == LIST_NOT_FOUND_MSG


def test_removing_game_from_non_existent_list_returns_404(users, games, rem_game_request):
    """Alice tenta remover um jogo de uma lista que não existe"""

    user = users["Alice"]
    game_id = games["roblox"][0]
    list_in = BaseList(list_id = "inexistent")

    rem_response = rem_game_request(user, list_in, game_id)
    assert rem_response.status_code == 404, rem_response.json()
    assert rem_response.json() == LIST_NOT_FOUND_MSG


def test_adding_game_only_affects_own_list(users, games, create_list, add_game_request):
    """Alice e Bernardo criam suas próprias listas, Alice adiciona um jogo, isso não deve afetar a lista de Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]
    game_id = games["mario"][0]

    list_user1 = create_list(user1)
    list_user2 = create_list(user2)

    add_response = add_game_request(user1, list_user1, game_id)
    assert add_response.status_code == 200
    assert_game_in_list(user1, list_user1, game_id)
    assert_game_not_in_list(user2, list_user2, game_id)


def test_adding_games_to_list_you_dont_own_returns_403(users, games, create_list, save_list_request, add_game_request):
    """Alice cria uma lista, Bernardo salva a lista, Bernardo tenta adicionar um jogo a lista de Alice"""

    user1, user2 = users["Alice"], users["Bernardo"]
    game_id = games["mario"][0]
    list_user1 = create_list(user1)

    save_list_response = save_list_request(user2, list_user1)
    assert save_list_response.status_code == 200, save_list_response.json()
    assert_save(user2, list_user1)

    add_list_response = add_game_request(user2, list_user1, game_id)
    assert add_list_response.status_code == 403, add_list_response.json()
    assert add_list_response.json() == LACK_OF_LIST_OWNERSHIP_MSG
    assert_game_not_in_list(user1, list_user1, game_id)


def test_adding_the_same_game_twice_returns_409(users, games, create_list, add_game_request):
    """Alice cria uma lista e tenta adicionar o mesmo game a ela 2 vezes"""

    user1 = users["Alice"]
    game_id = games["mario"][0]
    list_in = create_list(user1)

    response = add_game_request(user1, list_in, game_id)
    assert response.status_code == 200, response.json()

    duplicate_response = add_game_request(user1, list_in, game_id)
    assert duplicate_response.status_code == 409, response.json()
    assert duplicate_response.json() == {"message": "Esse game já está na lista!"}


def test_removing_the_same_game_twice_returns_200(users, games, create_list, add_game_request, rem_game_request):
    """Alice cria uma lista adiciona um game a ela, e depois o remove 2 vezes"""
    
    user1 = users["Alice"]
    game_id = games["mario"][0]
    list_in = create_list(user1)

    response = add_game_request(user1, list_in, game_id)
    assert response.status_code == 200, response.json()

    response = rem_game_request(user1, list_in, game_id)
    assert response.status_code == 200, response.json()

    response = rem_game_request(user1, list_in, game_id)
    assert response.status_code == 200, response.json()
    
