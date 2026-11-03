from .utils import *

CANT_UNSAVE_CREATED_LIST = {"message": "O usuário está tentando dessalvar sua própria lista!"}

def test_creating_automatically_saves(users, create_list):
    """Alice cria uma lista, o que salva automaticamente a lista de Alice"""

    user = users["Alice"]
    list_in = create_list(user)
    assert_save(user, list_in)


def test_saving_and_unsaving_list_returns_200(users, create_list, save_list_request, unsave_list_request):
    """Alice cria uma lista publica, Bernardo salva e depois dessalva a lista de Alice"""

    saver, creator = users["Bernardo"], users["Alice"]
    list_in = create_list(creator)

    save_response = save_list_request(saver, list_in)
    assert save_response.status_code == 200, save_response.json()
    assert save_response.json() == SUCCESS_SAVING_MSG
    assert_save(saver, list_in)

    unsave_response = unsave_list_request(saver, list_in)
    assert unsave_response.status_code == 200, unsave_response.json()
    assert unsave_response.json() == SUCCEESS_UNSAVING_MSG
    assert_unsave(saver, list_in)


def test_saving_private_list_returns_403(users, create_list, save_list_request):
    """Alice cria uma lista privada, Bernardo tenta salvar a lista de Alice"""

    saver, creator = users["Bernardo"], users["Alice"]
    list_in = create_list(creator, privacy=True)

    save_response = save_list_request(saver, list_in)
    assert save_response.status_code == 403, save_response.json()
    assert save_response.json() == PRIVATE_LIST_MSG
    assert_unsave(saver, list_in)


def test_saving_non_existent_list_returns_404(users, save_list_request, unsave_list_request):
    """Alice tenta salvar e desalvar uma lista que não existe"""

    user = users["Alice"]
    list_in = BaseList(list_id = "inexistent")

    save_response = save_list_request(user, list_in)
    assert save_response.status_code == 404, save_response.json()
    assert save_response.json() == LIST_NOT_FOUND_MSG

    unsave_response = unsave_list_request(user, list_in)
    assert unsave_response.status_code == 404, unsave_response.json()
    assert unsave_response.json() == LIST_NOT_FOUND_MSG


def test_unsaving_your_own_list_returns_403(users, create_list, unsave_list_request):
    """Alice cria uma lista e tenta dessalvala""" 

    user1 = users["Alice"]
    list_in = create_list(user1)

    unsave_response = unsave_list_request(user1, list_in)
    assert unsave_response.status_code == 403, unsave_response.json()
    assert unsave_response.json() == CANT_UNSAVE_CREATED_LIST


def test_blocking_stops_saves(users, block_request, create_list, save_list_request):
    """Alice cria uma lista publica, Alice bloqueia Bernado, Bernardo tenta salvar a lista de Alice"""

    user1, user2 = users["Bernardo"], users["Alice"]
    list_in = create_list(user2, privacy=Clearence.ANY)

    block_response = block_request(user2, user1, True)
    assert block_response.status_code == 200, block_response.json()
    assert_block(user2, user1)

    save_response = save_list_request(user1, list_in)
    assert save_response.status_code == 433, save_response.json()
    assert save_response.json() == BLOCKED_BY_LIST_OWNER_MSG
    assert_unsave(user1, list_in)


@pytest.mark.rawg
def test_creating_list_with_invalid_games_returns_invalid_games_and_200(users, games):
    """Alice cria uma lista, mas um dos game-ids para inserir na lista não são válidos"""

    user = users["Alice"]
    invalid_games = [1, 2]
    games_list = games["mario"] + invalid_games
    list_in = BaseList(1, first_games=games_list)

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


@pytest.mark.slow
def test_list_saving_pagination(pagination_tests, users, create_list, save_list_request):
    """Alice salva várias listas de Bernardo"""

    def seed_order(saver: BaseUser, total: int, order: str = ""):
        """Cria várias listas em ordens diferentes"""

        list_names = [f"List{i+1}" for i in range(total-2)]
        create_list.cleanup()

        new_lists = [create_list(users["Bernardo"], list_name = l) for l in list_names]

        for nl in new_lists:
            response = save_list_request(saver, nl)
            assert response.status_code == 200, response.json()

        complete_new_lists = [
            BaseList(list_id=completed_list_id(saver), name="Jogos Completados"),
            BaseList(list_id=favorites_list_id(saver), name="Jogos Favoritos"),
        ] + new_lists

        complete_list_names = [cnl.name for cnl in complete_new_lists]
            
        if ("!" in order) or (len(order) == 0):
            complete_list_names.reverse()

        return complete_list_names

    def seed_search(saver: BaseUser, total: int, search: str):
        """Alice salva várias listas de Bernardo, para que apareça no search depois"""

        searched_list_names = [ (search + "_" * i) for i in range(total)]
        unsearched_list_names = ["Esportes", "Aventura"]
        all_list_names = searched_list_names + unsearched_list_names
        create_list.cleanup()

        for l in all_list_names:
            nl = create_list(users["Bernardo"], list_name = l)
            response = save_list_request(saver, nl)
            assert response.status_code == 200, response.json()

        searched_list_names.reverse()

        return {"match": searched_list_names, "no_match": unsearched_list_names}

    pagination_tests(
        user = users["Alice"],
        url = BASE_URL_LISTS + f"/save",
        seed_order = seed_order,
        seed_search = seed_search,
        seed_obj = "name",
        content = ["list_id", "name", "creator", "saves_count", "cover_picture", "rel"],
        orders = ["!created_at", "created_at", "!name", "name", ""],
        searches = ["Playstation", "Minecraft"],
        require_login = False
    )
    

