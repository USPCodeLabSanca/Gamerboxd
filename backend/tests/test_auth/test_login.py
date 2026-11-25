import pytest


@pytest.mark.parametrize("identifier_type", ["email", "username"])
@pytest.mark.parametrize("identifier_is_valid, password_is_valid, expected_status", [
    pytest.param(True, True, 200, id="correct-credentials"),
    pytest.param(True, False, 400, id="wrong-password"),
    pytest.param(False, True, 400, id="wrong-identifier"),
    pytest.param(False, False, 400, id="wrong-credentials"),
])
def test_login_checks_credentials(
    users, login_request, identifier_type, identifier_is_valid, password_is_valid, expected_status
):
    """Verifica o login com email ou username e diferentes credenciais."""

    login_account = users("LoginTestUser")
    login_identifier = getattr(login_account, identifier_type)

    if not identifier_is_valid:
        login_identifier = "missing@example.com" if identifier_type == "email" else "missing-user"

    login_password = login_account.pwd if password_is_valid else "WrongPassword1!"
    login_response = login_request(login_identifier, login_password)

    assert login_response.status_code == expected_status, login_response.json()

    if expected_status == 200:
        assert login_response.json()["user_id"] == login_account.user_id
        assert set(login_response.cookies.get_dict()) == {"access-token", "refresh-token"}
    else:
        assert login_response.cookies.get_dict() == {}
        assert login_response.headers.get("Set-Cookie") is None


def test_logging_in_twice_to_same_account_succeeds(users, login_request):
    """Verifica que a mesma conta pode fazer login duas vezes."""

    login_account = users("RepeatedLoginUser")

    first_login = login_request(login_account.email, login_account.pwd)
    second_login = login_request(login_account.email, login_account.pwd)

    for login_response in (first_login, second_login):
        assert login_response.status_code == 200, login_response.json()
        assert login_response.json()["user_id"] == login_account.user_id


def test_logging_in_to_another_account_switches_user(users, login_request):
    """Verifica que o login em outra conta retorna o usuário correspondente."""

    current_account = users("CurrentLoginUser")
    next_account = users("NextLoginUser")

    current_account_login = login_request(current_account.email, current_account.pwd)
    next_account_login = login_request(next_account.email, next_account.pwd)

    assert current_account_login.status_code == 200, current_account_login.json()
    assert current_account_login.json()["user_id"] == current_account.user_id
    assert next_account_login.status_code == 200, next_account_login.json()
    assert next_account_login.json()["user_id"] == next_account.user_id

    for cookie_name in ("access-token", "refresh-token"):
        assert current_account_login.cookies[cookie_name] != next_account_login.cookies[cookie_name]


def test_login_cookies_have_expected_attributes(users, login_request):
    """Verifica os atributos dos cookies definidos durante o login."""

    login_account = users("CookieLoginUser")
    login_response = login_request(login_account.email, login_account.pwd)

    assert login_response.status_code == 200, login_response.json()
    set_cookie_headers = login_response.raw.headers.getlist("Set-Cookie")
    assert {header.partition("=")[0] for header in set_cookie_headers} == {"access-token", "refresh-token"}

    for cookie_header in set_cookie_headers:
        cookie_attributes = cookie_header.lower()
        assert "; secure" in cookie_attributes
        assert "; httponly" in cookie_attributes
        assert "samesite=lax" in cookie_attributes