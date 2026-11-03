from .utils import *

CANT_EDIT_STANDARD_LIST = {"message": "Não é possível alterar esses detalhes dessa lista!"}
CANT_DELETE_STANDARD_LIST = {"message": "Não é possível deletar essa lista!"}
CANT_ADD_TO_STANDARD_LIST = {"message": "Não é possível adicionar games a esta lista sem escrever ou editar uma review!"}
CANT_REM_FROM_STANDARD_LIST = {"message": "Não é possível remover games desta lista sem deletar ou editar sua review!"}


def test_creating_account_automatically_creates_standard_lists(create_account):
    """Um usuário novo cria uma conta, o que deve criar suas listas padrão automaticamente"""

    user = create_account("User1")
    user_lists = view_created_lists(user)

    assert any(ul["name"] == "Jogos Favoritos" for ul in user_lists)
    assert any(ul["name"] == "Jogos Completados" for ul in user_lists)


@pytest.mark.parametrize("new_name, old_desc", [
    ("Jogos Prediletos", "Meus games favoritos"),
    ("Jogos Terminados", "Meus games completados"),
])
def test_edit_standard_list_name_returns_435(users, edit_list_request, new_name, old_desc):
    """Alice tenta trocar o nome das suas listas padrão"""

    creator = users["Alice"]
    list_edit = BaseList(
        list_id = favorites_list_id(creator) if "favoritos" in old_desc else completed_list_id(creator),
        name=new_name,
        description=old_desc
    )

    edit_response = edit_list_request(creator, list_edit)
    assert edit_response.status_code == 435, edit_response.json()
    assert edit_response.json() == CANT_EDIT_STANDARD_LIST


@pytest.mark.parametrize("old_name, new_desc", [
    ("Jogos Favoritos", "Gostei desses jogos"),
    ("Jogos Completados", "Terminei esses jogos"),
])
def test_edit_standard_list_desc_returns_435(users, edit_list_request, old_name, new_desc):
    """Alice tenta trocar a descrição das suas listas padrão"""

    creator = users["Alice"]
    list_edit = BaseList(
        list_id = favorites_list_id(creator) if "Favoritos" in old_name else completed_list_id(creator), 
        name = old_name,
        description = new_desc
    )

    edit_response = edit_list_request(creator, list_edit)
    assert edit_response.status_code == 435, edit_response.json()
    assert edit_response.json() == CANT_EDIT_STANDARD_LIST


@pytest.mark.parametrize("old_name, old_desc, new_privacy", [
    ("Jogos Favoritos", "Meus games favoritos", Clearence.ANY),
    ("Jogos Favoritos", "Meus games favoritos", Clearence.FOLLOWED),
    ("Jogos Completados", "Meus games completados", Clearence.ANY),
    ("Jogos Completados", "Meus games completados", Clearence.FOLLOWED)
])
def test_edit_standard_list_privacy_returns_200(users, edit_list_request, old_name, old_desc, new_privacy):
    """Alice troca a privacidade das suas listas padrão"""

    creator = users["Alice"]
    list_edit = BaseList(
        list_id = favorites_list_id(creator) if "Favoritos" in old_name else completed_list_id(creator),
        name = old_name,
        description = old_desc,
        privacy = new_privacy
    )

    edit_response = edit_list_request(creator, list_edit)
    assert edit_response.status_code == 200, edit_response.json()
    assert edit_response.json()["privacy"] == new_privacy


@pytest.mark.rawg
@pytest.mark.parametrize("name", ["Jogos Favoritos", "Jogos Completados"])
def test_adding_games_to_standard_lists_directly_returns_435(users, games, add_game_request, name):
    """Alice tenta adicionar game as suas listas padrão sem escrever ou editar uma review"""

    creator = users["Alice"]
    game_id = games["mario"][0]
    standard_list = BaseList(
        list_id = favorites_list_id(creator) if "Favoritos" in name else completed_list_id(creator), 
        name = name
    )

    response = add_game_request(creator, standard_list, game_id)
    assert response.status_code == 435, response.json()
    assert response.json() == CANT_ADD_TO_STANDARD_LIST


@pytest.mark.rawg
@pytest.mark.parametrize("names", 
    [["Jogos Favoritos"], 
     ["Jogos Completados"],
     ["Jogos Favoritos", "Jogos Completados"],
     []
    ])
def test_adding_games_to_standard_lists_with_review_creation(users, games, create_review, names):
    """Alice adiciona game as suas listas padrão escrevendo uma review"""

    creator = users["Alice"]
    game_id = games["mario"][0]
    standard_lists = [
        BaseList(list_id = favorites_list_id(creator), name = "Jogos Favoritos"),
        BaseList(list_id = completed_list_id(creator), name = "Jogos Completados")
    ]

    review_creation_kwargs = {
        "liked": any("Favoritos" in name for name in names),
        "completed": any("Completados" in name for name in names)
    }

    create_review(creator, game_id, **review_creation_kwargs)

    for l in standard_lists:
        assert_game_in_list(creator, l, game_id) if l.name in names else assert_game_not_in_list(creator, l, game_id)


@pytest.mark.rawg
@pytest.mark.parametrize("names", 
    [["Jogos Favoritos"], 
     ["Jogos Completados"],
     ["Jogos Favoritos", "Jogos Completados"],
     []
    ])
def test_adding_games_to_standard_lists_with_review_update(users, games, create_review, edit_review_request, names):
    """Alice adiciona game as suas listas padrão editando uma review"""

    creator = users["Alice"]
    game_id = games["mario"][0]
    standard_lists = [
        BaseList(list_id = favorites_list_id(creator), name = "Jogos Favoritos"),
        BaseList(list_id = completed_list_id(creator), name = "Jogos Completados")
    ]

    review_creation_kwargs = {
        "liked": not any("Favoritos" in name for name in names),
        "completed": not any("Completados" in name for name in names)
    }

    review = create_review(creator, game_id, **review_creation_kwargs)
    review.liked = not review.liked
    review.completed = not review.completed

    response = edit_review_request(creator, review)
    assert response.status_code == 200, response.json()

    for l in standard_lists:
        assert_game_in_list(creator, l, game_id) if l.name in names else assert_game_not_in_list(creator, l, game_id)    


@pytest.mark.rawg
@pytest.mark.parametrize("name", ["Jogos Favoritos", "Jogos Completados"])
def test_removing_games_directly_from_standard_lists_returns_435(users, games, rem_game_request, create_review, name):
    """Alice tenta remover game das suas listas padrão sem deletar ou editar uma review"""

    creator = users["Alice"]
    game_id = games["mario"][0]
    standard_list = BaseList(
        list_id = favorites_list_id(creator) if "Favoritos" in name else completed_list_id(creator), 
        name = name
    )

    review_creation_kwargs = {
        "liked": "Favoritos" in name,
        "completed": "Completados" in name
    }

    create_review(creator, game_id, **review_creation_kwargs)

    response = rem_game_request(creator, standard_list, game_id)
    assert response.status_code == 435, response.json()
    assert response.json() == CANT_REM_FROM_STANDARD_LIST


@pytest.mark.rawg
@pytest.mark.parametrize("names", 
    [["Jogos Favoritos"], 
     ["Jogos Completados"],
     ["Jogos Favoritos", "Jogos Completados"],
     []
    ])
def test_removing_games_from_standard_lists_with_review_deletion(users, games, create_review, names):
    """Alice remove game das suas listas padrão deletando uma review"""

    creator = users["Alice"]
    game_id = games["mario"][0]
    standard_lists = [
        BaseList(list_id = favorites_list_id(creator), name = "Jogos Favoritos"),
        BaseList(list_id = completed_list_id(creator), name = "Jogos Completados")
    ]

    review_creation_kwargs = {
        "cleanup": False,
        "liked": any("Favoritos" in name for name in names),
        "completed": any("Completados" in name for name in names)
    }

    review = create_review(creator, game_id, **review_creation_kwargs)
    for l in standard_lists:
        assert_game_in_list(creator, l, game_id) if l.name in names else assert_game_not_in_list(creator, l, game_id) 

    response = requests.delete(BASE_URL_REVIEWS + f"/{review.review_id}", cookies = creator.cookies)
    assert response.status_code == 200, response.json()

    for l in standard_lists:
        assert_game_not_in_list(creator, l, game_id)


@pytest.mark.rawg
@pytest.mark.parametrize("names", 
    [["Jogos Favoritos"], 
     ["Jogos Completados"],
     ["Jogos Favoritos", "Jogos Completados"],
     []
    ])
def test_removing_games_from_standard_lists_with_review_update(users, games, create_review, edit_review_request, names):
    """Alice tenta remover game das suas listas padrão editando uma review"""

    creator = users["Alice"]
    game_id = games["mario"][0]
    standard_lists = [
        BaseList(list_id = favorites_list_id(creator), name = "Jogos Favoritos"),
        BaseList(list_id = completed_list_id(creator), name = "Jogos Completados")
    ]

    review_creation_kwargs = {
        "liked": any("Favoritos" in name for name in names),
        "completed": any("Completados" in name for name in names)
    }

    review = create_review(creator, game_id, **review_creation_kwargs)
    review.liked = not review.liked
    review.completed = not review.completed

    response = edit_review_request(creator, review)
    assert response.status_code == 200, response.json()

    for l in standard_lists:
        assert_game_not_in_list(creator, l, game_id) if l.name in names else assert_game_in_list(creator, l, game_id)


@pytest.mark.parametrize("name", ["Jogos Favoritos", "Jogos Completados"])
def test_deleting_standard_lists_returns_435(users, name):
    """Alice tenta deletar suas listas padrão"""

    creator = users["Alice"]
    list_id = favorites_list_id(creator) if "Favoritos" in name else completed_list_id(creator)

    response = requests.delete(BASE_URL_LISTS + f"/{list_id}", cookies=creator.cookies)
    assert response.status_code == 435, response.json()
    assert response.json() == CANT_DELETE_STANDARD_LIST
