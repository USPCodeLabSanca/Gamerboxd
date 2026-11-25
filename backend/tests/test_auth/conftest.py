import pytest
import requests

from ..utils import BASE_URL


@pytest.fixture
def login_request():
    """Fornece uma função para enviar uma solicitação de login."""

    def _login(email_or_username: str, password: str):
        return requests.post(
            BASE_URL + "/auth/login",
            json={"email_or_username": email_or_username, "password": password}
        )

    return _login
