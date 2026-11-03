from .utils import *


def base_list(num:int, **overrides):
    """Payload padrão de uma lista"""

    list_in = {"name": f"list_{num}", "privacy": 40, "first_games": []}

    list_in.update(overrides)
    return list_in


new_lists = [
    # Testes funcionais
    (base_list(1, description="list1", privacy=10), 200,  SUCCESS_CREATING_MSG),
    (base_list(2, description="list2"), 200,  SUCCESS_CREATING_MSG),
    (base_list(3, privacy=10), 200,  SUCCESS_CREATING_MSG),
    (base_list(4), 200, SUCCESS_CREATING_MSG),
    (base_list(5, name="a"), 200, SUCCESS_CREATING_MSG),
    (base_list(6, description="a"), 200, SUCCESS_CREATING_MSG),

    # Testes de erros do usuário na hora de criar conta
    (base_list(1), 409, LIST_NAME_TAKEN("list_1")),
    (base_list(8, name="list6"*10), 400, LIST_NAME_TOO_BIG),
    (base_list(9, name="  "), 400, LIST_NAME_BLANK),
    (base_list(10, description="list8"*61), 400,  LIST_DESC_TOO_BIG),
    (base_list(11, description="  "), 400,  LIST_DESC_BLANK),

    # Testes de schema inválido/mal formatado
    (base_list(12, name=8), 422, None),
    (base_list(13, name=None), 422, None),
    ({"list_name": "list_10"}, 422, None),
    (base_list(14, description=11), 422, None),
    (base_list(15, privacy="private"), 422, None),
    (base_list(16, privacy=None), 422, None),  
]


@pytest.mark.parametrize("list_in,expected_status,expected_body", new_lists)
def test_new_lists(users, list_in, expected_status, expected_body):

    user = users["Alice"]
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


@pytest.mark.rawg
def test_creating_list_with_games_returns_200(users, games):
    """Alice cria uma lista já enviando os primeiros games dela"""

    user = users["Alice"]
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


@pytest.mark.rawg
def test_creating_list_with_invalid_games_returns_invalid_games_and_200(users, games):
    """Alice cria uma lista, mas um dos game-ids para inserir na lista não são válidos"""

    user = users["Alice"]
    invalid_games = [1, 2]
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


@pytest.mark.slow
def test_list_creation_pagination(pagination_tests, users, create_list, edit_list_request):
    """Alice cria várias listas"""

    def seed_order(creator: BaseUser, total: int, order: str = ""):
        """Cria várias listas em ordens diferentes"""

        list_names = [f"List{i+1}" for i in range(total-2)]
        complete_list_names = ["Jogos Completados", "Jogos Favoritos"] + list_names
        create_list.cleanup()

        new_lists = [create_list(creator, list_name = l) for l in list_names]
        complete_new_lists = [
            BaseList(list_id=completed_list_id(creator), name="Jogos Completados", description="Meus games completados", privacy=Clearence.OWNER),
            BaseList(list_id=favorites_list_id(creator), name="Jogos Favoritos", description="Meus games favoritos", privacy=Clearence.OWNER),
        ] + new_lists

        if ("updated" in order) or (len(order) == 0):
            random.shuffle(complete_new_lists)
            for nl in complete_new_lists:
                nl.privacy = Clearence.FOLLOWED
                response = edit_list_request(creator, nl)
                assert response.status_code == 200, response.json()

        complete_list_names = [nl.name for nl in complete_new_lists]
            
        if ("!" in order) or (len(order) == 0):
            complete_list_names.reverse()

        return complete_list_names

    def seed_search(creator: BaseUser, total: int, search: str):
        """Cria várias listas, para que apareça no search depois"""

        searched_list_names = [ (search + "_" * i) for i in range(total)]
        unsearched_list_names = ["Esportes", "Aventura"]
        all_list_names = searched_list_names + unsearched_list_names
        create_list.cleanup()

        for l in all_list_names:
            create_list(creator, list_name = l)

        searched_list_names.reverse()

        return {"match": searched_list_names, "no_match": unsearched_list_names}

    pagination_tests(
        user = users["Alice"],
        url = BASE_URL_LISTS + f"/created/{users["Alice"].user_id}",
        seed_order = seed_order,
        seed_search = seed_search,
        seed_obj = "name",
        content = ["list_id", "name", "creator", "saves_count", "cover_picture", "rel"],
        orders = ["!created_at", "created_at", "!name", "name", "!updated_at", "updated_at", ""],
        searches = ["Playstation", "Minecraft"],
        require_login = False
    )
