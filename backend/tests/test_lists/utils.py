from ..utils import *

SUCCESS_CREATING_MSG = {"message":"Lista criada com sucesso!", "list_id": "abc"}
SUCCESS_DELETING_MSG = {"message":"Lista deletada com sucesso!"}

SUCCESS_SAVING_MSG = {"message": "Lista salva com sucesso!"}
SUCCEESS_UNSAVING_MSG = {"message": "Lista dessalvada com sucesso"}
CANT_UNSVAE_CREATED_LIST = {"message": "Não é possível dessalvar sua própria lista, apenas deletá-la!"}

SUCCESS_ADDING_MSG = {"message": "Jogo adicionado à lista com sucesso"}
SUCCEESS_REMOVING_MSG = {"message": "Jogo removido da lista com sucesso"}

LIST_NOT_FOUND_MSG = {"message": "Lista não encontrada!"}
USER_NOT_FOUND_MSG = {"message": "Usuário não encontrado!"}

LIST_NAME_TAKEN = lambda name: {"message": f'O usuário já possui uma lista com o nome "{name}"!'}
LIST_NAME_TOO_BIG = {"message": "O nome da lista não pode exceder 45 caracteres!"}
LIST_NAME_BLANK = {"message": "O nome da lista não pode ser apenas espaço vazio!"}

LIST_DESC_TOO_BIG = {"message": "A descrição da lista não pode exceder 280 caracteres!"}
LIST_DESC_BLANK = {"message": "A descrição da lista não pode ser apenas espaço vazio!"}

PRIVATE_LIST_MSG = {"message": "Essa lista é privada!"}
LACK_OF_LIST_OWNERSHIP_MSG = {"message": "Apenas o autor da lista pode realizar esta ação!"}
BLOCKED_BY_LIST_OWNER_MSG = {"message": "O usuário está bloqueado pelo autor da lista!"}


def assert_privacy(user: BaseUser, list_in: BaseList, privacy: bool):
    """Garante a privacidade de uma lista no DB"""

    response = requests.get(
        url=BASE_URL_LISTS + f"/{list_in.list_id}",
        cookies=user.cookies
    )

    assert response.status_code == 200, response.json()
    assert response.json()["privacy"] == privacy


def view_list_saves(user: BaseUser):
    """Retorna as listas salvas por um usuário"""

    cookies = user.cookies
    saved_lists = []

    response = requests.get(BASE_URL_LISTS + "/save/lists", cookies=cookies)
    assert response.status_code == 200, response.json()
    response_json = response.json()
    saved_lists += response_json["content"]

    while response_json["next_url"] != None:
        response = requests.get(response_json["next_url"], cookies=cookies)
        assert response.status_code == 200, response.json()
        response_json = response.json()
        saved_lists += response_json["content"]

    return saved_lists


def assert_save(user: BaseUser, list_in: BaseList):
    """Garante que o usuário salvou a lista em sua biblioteca"""

    saved_lists = view_list_saves(user)
    assert any([list_in.list_id == sl["list_id"] for sl in saved_lists])


def assert_unsave(user: BaseUser, list_in: BaseList):
    """Garante que o usuário não salvou a lista em sua biblioteca"""

    saved_lists = view_list_saves(user)
    assert all([list_in.list_id != sl["list_id"] for sl in saved_lists])


def view_list_games(user: BaseUser, list_in: BaseList):
    """Retorna os games que estão na lista do usuário"""

    cookies = user.cookies
    list_games = []

    response = requests.get(f"{BASE_URL_LISTS}/game/{list_in.list_id}?page_size=30", cookies=cookies)
    assert response.status_code == 200, response.json()
    response_json = response.json()
    list_games += response_json["content"]

    while response_json["next_url"] != None:
        response = requests.get(response_json["next_url"], cookies=cookies)
        assert response.status_code == 200, response.json()
        response_json = response.json()
        list_games += response_json["content"]

    return list_games


def assert_game_in_list(user: BaseUser, list_in: BaseList, game_id: int):
    """Garante que um game pertence a uma lista"""

    games = view_list_games(user, list_in)
    assert any(g["game_id"] == game_id for g in games)


def assert_game_not_in_list(user: BaseUser, list_in: BaseList, game_id: int):
    """Garante que um game não pertence a uma lista"""

    games = view_list_games(user, list_in)
    assert all(g["game_id"] != game_id for g in games)


def view_created_lists(user: BaseUser):
    """Retorna as listas criadas pelo usuário"""

    cookies = user.cookies
    user_lists = []

    response = requests.get(f"{BASE_URL_LISTS}/created/{user.user_id}?page_size=40", cookies=cookies)
    assert response.status_code == 200, response.json()
    response_json = response.json()
    user_lists += response_json["content"]

    while response_json["next_url"] != None:
        response = requests.get(response_json["next_url"], cookies=cookies)
        assert response.status_code == 200, response.json()
        response_json = response.json()
        user_lists += response_json["content"]

    return user_lists


def favorites_list_id(user: BaseUser):
    """Retorna o list_id da lista de favoritos do usuário"""

    created_lists = view_created_lists(user)

    for cl in created_lists:
        if cl["name"] == "Jogos Favoritos":
            return cl["list_id"]

    return None


def completed_list_id(user: BaseUser):
    """Retorna o list_id da lista de completados do usuário"""

    created_lists = view_created_lists(user)

    for cl in created_lists:
        if cl["name"] == "Jogos Completados":
            return cl["list_id"]

    return None


