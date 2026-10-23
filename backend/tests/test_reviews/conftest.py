from .utils import *


@pytest.fixture()
def create_review():
    """Insere uma review no DB
    se o cleanup for True, depois a remove do DB"""

    responses = []

    # Insere a review no DB
    def _create_review(user: BaseUser, game_id: int, privacy: int = Clearence.ANY, cleanup: bool = True):
        review = BaseReview(
            game_id = game_id,
            rating_num = 3.5,
            rating_text = "Muito bom, recomendo!",
            liked = True,
            privacy = privacy,
            time_played = 15,
            completed = True,
        )

        create_resp = requests.post(url=BASE_URL_REVIEWS, json=asdict(review), cookies=user.cookies)

        if cleanup:
            assert create_resp.status_code == 200, create_resp.json()
            assert "review_id" in create_resp.json().keys()
            review_id = create_resp.json()["review_id"]
            responses.append({"cookies": user.cookies, "review_id": review_id})
            review.review_id = review_id

        return review

    yield _create_review

    # Remove a review do DB
    for r in responses:
        del_resp = requests.delete(url=BASE_URL_REVIEWS + f"/{r["review_id"]}", cookies=r["cookies"])
        assert del_resp.status_code == 200
        assert del_resp.json() == SUCCESS_DELETING_MSG


@pytest.fixture
def edit_review_request():
    """Faz o request para editar uma review de usuário"""

    # Tenta editar a review no DB
    def _edit_review_request(user: BaseUser, review: BaseReview):
        review_copy = asdict(copy.copy(review))
        id = review_copy.pop("review_id")
        return requests.put(f"{BASE_URL_REVIEWS}/{id}", cookies=user.cookies, json=review_copy)

        
    return _edit_review_request


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
