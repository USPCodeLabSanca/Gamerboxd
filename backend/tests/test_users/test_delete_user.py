from . import BASE_URL, pytest, requests

def delete_account(user: dict):
    user_without_cookies = user.copy()
    cookies = user_without_cookies.pop("cookies", None)

    return requests.delete(f"{BASE_URL}/user", cookies=cookies, json = user_without_cookies)