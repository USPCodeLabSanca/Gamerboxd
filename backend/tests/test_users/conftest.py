import copy
from dataclasses import asdict
import pytest
import requests

from ..utils import BASE_URL_USERS, BaseUser


@pytest.fixture
def edit_user_request():
    """Faz o request para editar uma conta de usuário. 
    Se reset for um BaseUser significa que vai resetar para esse BaseUser no DB depois"""

    accounts = []

    # Tenta editar a conta no DB
    def _edit_user(user: dict, reset: BaseUser | None = None):
        user_copy = user.copy()
        cookies = user_copy.pop("cookies")

        edit_response = requests.put(BASE_URL_USERS, cookies=cookies, json=user_copy)
        if reset is not None:
            assert edit_response.status_code == 200, edit_response.json()
            accounts.append({"reset": reset})
        return edit_response

    def _reset():
        while len(accounts) > 0:
            account = accounts.pop()
            reset_copy = asdict(copy.copy(account["reset"]))
            cookies = reset_copy.pop("cookies")
            reset_resp = requests.put(BASE_URL_USERS, cookies=cookies, json=reset_copy)
            assert reset_resp.status_code == 200, reset_resp.json()

    yield _edit_user

    _reset()