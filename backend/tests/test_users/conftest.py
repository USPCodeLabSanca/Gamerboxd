from .utils import BASE_URL, requests, pytest


@pytest.fixture
def edit_user():
    """Faz um usuário editar sua conta. reset != None significa que vai reverter o DB depois"""
    response = []

    def _edit_user(user: dict, reset: dict = None):
        user_copy = user.copy()
        cookies = user_copy.pop("cookies", None)
        edit_resp = requests.put(f"{BASE_URL}", cookies=cookies, json=user_copy)
        response.append({"response": edit_resp, "reset": reset})
        return edit_resp

    yield _edit_user

    edit_resp = response[0]

    if (edit_resp["reset"] is not None) and (edit_resp["response"].status_code == 200):
        reset_copy = edit_resp["reset"].copy()
        cookies = reset_copy.pop("cookies", None)
        reset_resp = requests.put(f"{BASE_URL}", cookies=cookies, json=reset_copy)
        assert reset_resp.status_code == 200