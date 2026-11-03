from .utils import *


@pytest.fixture
def like_review_request():
    """Faz o request para dar like numa review
    Se o cleanup = True, vai apagar do DB depois que a função rodar"""

    responses = []

    # Tenta inserir o like no DB
    def _like_review_request(user: BaseUser, review: BaseReview, cleanup: bool = False):
        cookies, target = user.cookies, review.review_id
        like_resp = requests.post(f"{BASE_URL_REVIEWS}/like/{target}", cookies=cookies)

        if cleanup:
            assert like_resp.status_code == 200, like_resp.json()
            responses.append({"target": target, "cookies": cookies})

        return like_resp

    yield _like_review_request

    # Limpa do DB
    for r in responses:
        cookies, target = r["cookies"], r["target"]
        unlike_resp = requests.delete(f"{BASE_URL_REVIEWS}/like/{target}", cookies=cookies)
        assert unlike_resp.status_code == 200, unlike_resp.json()


@pytest.fixture
def unlike_review_request():
    """Faz o request para remover um like de uma review no DB"""

    # Tenta remover o like da review no DB
    def _unlike_review_request(user: BaseUser, review: BaseReview):
        return requests.delete(f"{BASE_URL_REVIEWS}/like/{review.review_id}", cookies = user.cookies)

    return _unlike_review_request
