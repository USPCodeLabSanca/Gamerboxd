import pytest
import requests

from ..utils import BaseUser, BaseReview, BASE_URL_REVIEWS


@pytest.fixture
def like_review_request():
    """Faz o request para dar like numa review
    Se o cleanup = True, vai apagar do DB depois que a função rodar"""

    likes = []

    def _like_review_request(user: BaseUser, review: BaseReview, cleanup: bool = False):
        """Tenta inserir o like no DB"""
        cookies, target = user.cookies, review.review_id
        like_response = requests.post(BASE_URL_REVIEWS + f"/like/{target}", cookies=cookies)

        if cleanup:
            assert like_response.status_code == 200, like_response.json()
            likes.append({"target": target, "cookies": cookies})

        return like_response

    def _cleanup():
        """Remove os likes inseridos até agora"""
        while len(likes) > 0:
            l = likes.pop()
            cookies, target = l["cookies"], l["target"]
            response = requests.delete(BASE_URL_REVIEWS + f"/like/{target}", cookies=cookies)
            assert response.status_code == 200, response.json()

    _like_review_request.cleanup = _cleanup

    yield _like_review_request

    _cleanup()


@pytest.fixture
def unlike_review_request():
    """Faz o request para remover um like de uma review no DB"""

    def _unlike_review_request(user: BaseUser, review: BaseReview):
        """Tenta remover o like da review no DB"""
        return requests.delete(BASE_URL_REVIEWS + f"/like/{review.review_id}", cookies=user.cookies)

    return _unlike_review_request


@pytest.fixture()
def get_review_request():
    """Faz o request para pegar os dados completos de uma review no DB"""

    def _get_review_request(user: BaseUser, review: BaseReview):
        return requests.get(BASE_URL_REVIEWS + f"/{review.review_id}", cookies=user.cookies)

    return _get_review_request


@pytest.fixture
def delete_review_request():
    """Faz o request para remover uma review do DB"""

    def _delete_review_request(user: BaseUser, review: BaseReview):
        return requests.delete(BASE_URL_REVIEWS + f"/{review.review_id}", cookies=user.cookies)

    return _delete_review_request


