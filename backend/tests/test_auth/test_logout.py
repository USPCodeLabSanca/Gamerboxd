import requests

from ..utils import BASE_URL

LOGOUT_SUCCESS_MSG = {"message": "Logout feito com sucesso!"}


def assert_cleared_cookies(logout_response):
    """Verifica que a resposta remove os cookies de autenticação."""

    set_cookie_headers = logout_response.raw.headers.getlist("Set-Cookie")
    assert {header.partition("=")[0] for header in set_cookie_headers} == {"access-token", "refresh-token"}

    for cookie_header in set_cookie_headers:
        cookie_value = cookie_header.split(";", 1)[0].partition("=")[2].strip('"')
        assert cookie_value == ""
        assert "max-age=0" in cookie_header.lower()


def test_logout_while_logged_in_returns_200_and_clears_cookies(users, login_request):
    """Verifica que o logout encerra uma sessão autenticada."""

    logout_account = users("LogoutTestUser")
    login_response = login_request(logout_account.email, logout_account.pwd)
    assert login_response.status_code == 200, login_response.json()

    logout_response = requests.delete(
        BASE_URL + "/auth/login",
        cookies=login_response.cookies.get_dict()
    )

    assert logout_response.status_code == 200, logout_response.json()
    assert logout_response.json() == LOGOUT_SUCCESS_MSG
    assert_cleared_cookies(logout_response)


def test_logout_while_not_logged_in_returns_200_and_clears_cookies():
    """Verifica que o logout também funciona sem sessão ativa."""

    logout_response = requests.delete(BASE_URL + "/auth/login")

    assert logout_response.status_code == 200, logout_response.json()
    assert logout_response.json() == LOGOUT_SUCCESS_MSG
    assert_cleared_cookies(logout_response)