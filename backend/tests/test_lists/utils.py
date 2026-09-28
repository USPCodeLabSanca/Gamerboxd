import pytest
import requests

BASE_URL = "http://127.0.0.1:8000/list"

SUCCESS_CREATING_MSG = {"message":"Lista criada com sucesso!"}
SUCCESS_DELETING_MSG = {"message":"Lista deletada com sucesso!"}
SUCCESS_SAVING_MSG = {"message": "Lista salva com sucesso!"}
SUCCEESS_UNSAVING_MSG = {"message": "Lista dessalvada com sucesso"}
SUCCESS_ADDING_MSG = {"message": "Jogo adicionado à lista com sucesso"}
SUCCEESS_REMOVING_MSG = {"message": "Jogo removido da lista com sucesso"}
LIST_NOT_FOUND_MSG = {"message": "Lista não encontrada!"}
USER_NOT_FOUND_MSG = {"message":"Usuário não encontrado!"}


def create_list(user: dict, list_name: str = None, privacy: bool = False):
    cookies = user["cookies"]
    list_in = {"name": list_name if list_name is not None else user["username"]}

    if privacy is not None:
        list_in["is_private"] = privacy

    response = requests.post(url=BASE_URL, json=list_in, cookies=cookies)
    assert response.status_code == 200
    assert response.json() == SUCCESS_CREATING_MSG

    return list_in


def delete_list(user: dict, list_in: dict):
    cookies = user["cookies"]
    response = requests.delete(url = BASE_URL + f"/{list_in["name"]}", cookies=cookies)
    assert response.status_code == 200
    assert response.json() == SUCCESS_DELETING_MSG


def set_privacy(user: dict, list_in: dict, privacy: bool):
    list_in["is_private"] = privacy

    response = requests.put(
        url=BASE_URL + f"/{list_in["name"]}",
        cookies=user["cookies"],
        json=list_in
    )

    assert response.status_code == 200, f"{response.json()}"


def assert_privacy(user: dict, list_in: dict, privacy: bool):
    list_in["is_private"] = False

    response = requests.get(
        url=BASE_URL + f"/{list_in["name"]}",
        cookies=user["cookies"]
    )

    assert response.status_code == 200
    assert response.json()["is_private"] == privacy


def assert_block(atv: dict, pas: dict):
    """Garante que atv bloqueou pas"""

    cookies = atv["cookies"]
    response = requests.get(f"{BASE_URL[:-5]}/user/block", cookies=cookies)
    response_json = response.json()
    assert any([f["username"] == pas["username"] for f in response_json["blocks"]])

