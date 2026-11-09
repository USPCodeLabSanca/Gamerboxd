import requests

from ..utils import BaseUser, BaseReview, BASE_URL_REVIEWS

SUCCESS_DELETING_MSG = {"message":"Review deletada com sucesso!"}

RATING_TEXT_TOO_BIG_MSG = {"message": "O texto da review não pode exceder 300 caracteres!"}
RATING_TEXT_BLANK_MSG = {"message": "O texto da review não pode ser apenas espaço vazio!"}
RATING_NUM_INVALID_MSG = {"message": "A avaliação numérica da review tem que estar entre 0 e 5, com step de 0.5!"}
REVIEW_ALREADY_EXISTS_MSG = {"message": "Você já possui uma review desse jogo!"}
REVIEW_PRIVACY_INVALID_MSG = {"message": "A privacidade da review não é um dos valores válidos!"}
TIME_PLAYED_INVALID_MSG = {"message": "O tempo de jogo não pode ser negativo!"}

PRIVATE_REVIEW_MSG = {"message": "Essa review é privada!"}
LACK_OF_REVIEW_OWNERSHIP_MSG = {"message": "Apenas o autor da review pode realizar essa ação!"}
BLOCKED_BY_REVIEW_OWNER_MSG = {"message": "O usuário está bloqueado pelo autor da review!"}
USER_BLOCKED_REVIEW_OWNER_MSG = {"message": "Não é possível ver detalhes da review um usuário antes de desbloqueá-lo!"}


def view_review_likes(user: BaseUser, review: BaseReview):
    """Retorna quem deu like na review do usuário"""

    cookies = user.cookies
    review_likes = []

    response = requests.get(BASE_URL_REVIEWS + f"/like/users/{review.review_id}", cookies=cookies)
    assert response.status_code == 200, response.json()
    review_likes += response.json()["content"]

    while response.json()["next_url"] != None:
        response = requests.get(response.json()["next_url"], cookies=cookies)
        assert response.status_code == 200, response.json()
        review_likes += response.json()["content"]

    return review_likes


def view_user_likes(user: BaseUser):
    """Retorna as reviews para quais o usuário deu like"""

    cookies = user.cookies
    user_likes = []

    response = requests.get(BASE_URL_REVIEWS + "/like/reviews", cookies=cookies)
    assert response.status_code == 200, response.json()
    user_likes += response.json()["content"]

    while response.json()["next_url"] != None:
        response = requests.get(response.json()["next_url"], cookies=cookies)
        assert response.status_code == 200, response.json()
        user_likes += response.json()["content"]

    return user_likes


def assert_review_like_by_review(atv: BaseUser, pas: BaseUser, review: BaseReview):
    """Garante que o atv deu like na review do pas, verificando todos os likes que a review recebeu"""

    review_likes = view_review_likes(pas, review)
    assert any(atv.user_id == rl["user_id"] for rl in review_likes)


def assert_review_like_by_user(atv: BaseUser, pas: BaseUser, review: BaseReview):
    """Garante que o atv deu like na review do pas, verificando todos os likes que o atv já deu"""

    user_likes = view_user_likes(atv, review)
    assert any((review.review_id == ul["review_id"]) and (pas.user_id == ul["creator"]["user_id"]) for ul in user_likes)


def assert_review_unlike_by_review(atv: BaseUser, pas: BaseUser, review: BaseReview):
    """Garante que o atv não deu like na review dos pas, verificando todos os likes que a review recebeu"""

    review_likes = view_review_likes(pas, review)
    assert all([atv.user_id != rl["user_id"] for rl in review_likes])


def assert_review_unlike_by_user(atv: BaseUser, pas: BaseUser, review: BaseReview):
    """Garante que o atv deu like na review do pas, verificando todos os likes que o atv já deu"""

    user_likes = view_user_likes(atv, review)
    assert all((review.review_id != ul["review_id"]) or (pas.user_id != ul["creator"]["user_id"]) for ul in user_likes)