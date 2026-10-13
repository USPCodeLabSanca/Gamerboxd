from .utils import *


@pytest.fixture
def create_list():
    """Insere uma lista no DB e depois a remove do DB"""

    response = []

    def _create_list(user: dict, list_name: str = None, privacy: bool = False):
        cookies = user["cookies"]
        list_in = {"name": list_name if list_name is not None else user["username"], "privacy": privacy}

        insert_resp = requests.post(url=BASE_URL, json=list_in, cookies=cookies)
        assert insert_resp.status_code == 200
        assert response.json() == SUCCESS_CREATING_MSG
        response.append({"response": insert_resp, "name": list_in["name"], "cookies": cookies})
        return list_in

    yield _create_list

    insert_resp = response[0]
    name, cookies = insert_resp["name"], cookies
    del_resp = requests.delete(url = BASE_URL + f"/{name}", cookies=cookies)
    assert del_resp.status_code == 200
    assert del_resp.json() == SUCCESS_DELETING_MSG


@pytest.fixture
def edit_list():
    """Faz um usuário editar sua lista. reset != None significa que vai reverter o DB depois"""

    response = []

    def _edit_list(user: dict, old_list_name: str, list_in: dict, reset: dict = None):
        # Tenta editar a lista no DB
        edit_resp = requests.put(f"{BASE_URL}/{old_list_name}", cookies=user["cookies"], json=list_in)
        response.append({"status_code": edit_resp, "reset": reset, "old_list_name": list_in["name"], "user": user})
        return edit_resp

    yield _edit_list

    edit_resp = response[0]

    # Reverte a lista depois de editar
    if (edit_resp["reset"] is not None) and (edit_resp["status_code"] == 200):
        old_list_name, user, reset = edit_resp["old_list_name"], edit_resp["user"], edit_resp["reset"]
        reset_resp = requests.put(f"{BASE_URL}/{old_list_name}", cookies=user["cookies"], json=reset)
        assert reset_resp.status_code == 200
