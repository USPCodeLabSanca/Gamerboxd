from ..utils import *

SUCCESS_CREATING_MSG = {"message":"Review criada com sucesso!", "id": "a"}
SUCCESS_DELETING_MSG = {"message":"Review deletada com sucesso!"}

CANT_CHANGE_GAME_MSG = {"message": "O jogo não pode ser alterado!"}
RATING_TEXT_TOO_BIG_MSG = {"message": "O texto da review não pode exceder 300 caractéres"}
REVIEW_ALREADY_EXISTS = {"message": "Você já possui uma review desse jogo!"}

SUCCESS_LIKING_MSG = {"message": "Like adicionado com sucesso!"}
SUCCESS_UNLIKING_MSG = {"message": "Like removido com sucesso!"}

PRIVATE_REVIEW_MSG = {"message": "Essa review é privada!"}
LACK_OF_REVIEW_OWNERSHIP_MSG = {"message": "Apenas o autor da review pode realizar essa ação!"}
BLOCKED_BY_REVIEW_OWNER_MSG = {"message": "O usuário está bloqueado pelo autor da review!"}

REVIEW_NOT_FOUND_MSG = {"message": "Review não encontrada!"}
USER_NOT_FOUND_MSG = {"message":"Usuário não encontrado!"}


def view_review_likes(user: BaseUser, review: BaseReview):
    """Retorna quem deu like na review do usuário"""

    cookies = user.cookies
    review_likes = []

    response = requests.get(BASE_URL_REVIEWS + "/like/users/" + review.review_id, cookies=cookies)
    assert response.status_code == 200, response.json()
    review_likes += response.json()["content"]

    while response.json()["next_page"] != None:
        response = requests.get(response.json()["next_page"], cookies=cookies)
        assert response.status_code == 200, response.json()
        review_likes += response.json()["content"]

    return review_likes


def assert_review_like(atv: BaseUser, pas: BaseUser, review: BaseReview):
    """Garante que o atv deu like na review do pas"""

    review_likes = view_review_likes(pas, review)
    assert any([atv.user_id == rl["user_id"] for rl in review_likes])


def assert_review_unlike(atv: BaseUser, pas: BaseUser, review: BaseReview):
    """Garante que o atv não deu like na review dos pas"""

    review_likes = view_review_likes(pas, review)
    assert all([atv.user_id != rl["user_id"] for rl in review_likes])