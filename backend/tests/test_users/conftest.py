from .utils import *


@pytest.fixture
def edit_user_request():
    """Faz o request para editar uma conta de usuário. 
    Se reset for um BaseUser significa que vai resetar para esse BaseUser no DB depois"""

    responses = []

    # Tenta editar a conta no DB
    def _edit_user(user: BaseUser, reset: BaseUser = None):
        user_copy = asdict(copy.copy(user))
        cookies = user_copy.pop("cookies")

        edit_resp = requests.put(f"{BASE_URL_USERS}", cookies=cookies, json=user_copy)
        if reset is not None:
            responses.append({"reset": reset})
        return edit_resp

    yield _edit_user

    # Reseta no DB
    for r in responses:
        reset_copy = asdict(copy.copy(r["reset"]))
        cookies = reset_copy.pop("cookies")
        reset_resp = requests.put(f"{BASE_URL_USERS}", cookies=cookies, json=reset_copy)
        assert reset_resp.status_code == 200, reset_resp.json()