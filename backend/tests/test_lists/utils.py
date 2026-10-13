import pytest
import requests

BASE_URL = "http://127.0.0.1:8000/list"

SUCCESS_CREATING_MSG = {"message":"Lista criada com sucesso!", "id": None}
SUCCESS_DELETING_MSG = {"message":"Lista deletada com sucesso!"}
SUCCESS_SAVING_MSG = {"message": "Lista salva com sucesso!"}
SUCCEESS_UNSAVING_MSG = {"message": "Lista dessalvada com sucesso"}
SUCCESS_ADDING_MSG = {"message": "Jogo adicionado à lista com sucesso"}
SUCCEESS_REMOVING_MSG = {"message": "Jogo removido da lista com sucesso"}
LIST_NOT_FOUND_MSG = {"message": "Lista não encontrada!"}
USER_NOT_FOUND_MSG = {"message": "Usuário não encontrado!"}
PRIVATE_LIST_MSG = {"message": "Essa lista é privada!"}
LACK_OF_LIST_OWNERSHIP_MSG = {"message": "Apenas o autor da lista pode realizar esta ação!"}
BLOCKED_BY_LIST_OWNER = {"message": "O usuário está bloqueado pelo autor da lista!"}


def create_list(user: dict, list_name: str = None, privacy: bool = False):
    cookies = user["cookies"]
    list_in = {"name": list_name if list_name is not None else user["username"]}

    if privacy is not None:
        list_in["is_private"] = privacy

    response = requests.post(url=BASE_URL, json=list_in, cookies=cookies)
    assert response.status_code == 200, response.json()
    assert response.json().keys() == SUCCESS_CREATING_MSG.keys()

    return {**list_in, "list_id": response.json()["id"]}


def delete_list(user: dict, list_in: dict):
    cookies = user["cookies"]
    response = requests.delete(url = BASE_URL + f"/{list_in["list_id"]}", cookies=cookies)
    assert response.status_code == 200
    assert response.json() == SUCCESS_DELETING_MSG


def set_privacy(user: dict, list_in: dict, privacy: bool):
    list_in["is_private"] = privacy

    response = requests.put(
        url=BASE_URL + f"/{list_in["list_id"]}",
        cookies=user["cookies"],
        json=list_in
    )

    assert response.status_code == 200, f"{response.json()}"


def assert_privacy(user: dict, list_in: dict, privacy: bool):
    list_in["is_private"] = False

    response = requests.get(
        url=BASE_URL + f"/{list_in["list_id"]}",
        cookies=user["cookies"]
    )

    assert response.status_code == 200
    assert response.json()["is_private"] == privacy


def assert_block(atv: dict, pas: dict):
    """Garante que atv bloqueou pas"""

    cookies = atv["cookies"]
    blocks = []

    response = requests.get(f"{BASE_URL[:-5]}/user/block", cookies=cookies)
    assert response.status_code == 200
    response_json = response.json()
    blocks += response_json["content"]

    while response_json["next_page"] != None:
        response = requests.get(response_json["next_page"], cookies=cookies)
        assert response.status_code == 200
        response_json = response.json()
        blocks += response_json["content"]

    assert any([b["username"] == pas["username"] for b in blocks])




