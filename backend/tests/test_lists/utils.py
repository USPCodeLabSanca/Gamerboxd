from . import *


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


def block(atv: dict, pas: dict):
    """Roda o bloqueio no backend"""

    target, cookies = pas["username"], atv["cookies"]
    return requests.post(f"{BASE_URL[:-5]}/user/block/{target}", cookies=cookies)


def assert_block(atv: dict, pas: dict):
    """Garante que atv bloqueou pas"""

    cookies = atv["cookies"]
    response = requests.get(f"{BASE_URL[:-5]}/user/block", cookies=cookies)
    response_json = response.json()
    assert any([f["username"] == pas["username"] for f in response_json["blocks"]])

