from .utils import *


def test_edit_review_valid_fields_returns_200(users, games, create_review, edit_review_request):
    """Alice cria uma review e edita a nota, se curtiu e o texto"""

    user = users["Alice"]
    game_id = games["mario"][0]

    review = create_review(user, game_id, True)

    review.rating_num = 10.0
    review.liked = False
    review.rating_text = "Novo texto"

    response = edit_review_request(user, review)
    assert response.status_code == 200, response.json()

    updated_review = response.json()
    assert updated_review["rating_num"] == review.rating_num
    assert updated_review["liked"] == review.liked
    assert updated_review["rating_text"] == review.rating_text


def test_edit_review_not_found_returns_404(users, games, create_review, edit_review_request):
    """Alice tenta editar uma review de um jogo que ele nunca avaliou"""

    user = users["Alice"]
    game_id = games["mario"][0]

    review = create_review(user, game_id, True)

    review.review_id = "abc"

    response = edit_review_request(user, review)
    assert response.status_code == 404, response.json()
    assert response.json() == REVIEW_NOT_FOUND_MSG


def test_edit_review_rating_text_return_200(users, games, create_review, edit_review_request):
    """Alice edita apenas o texto da sua review"""

    user = users["Alice"]
    game_id = games["GTA"][0]

    review = create_review(user, game_id, True)
    review.rating_text = "Novo texto"

    response = edit_review_request(user, review)
    assert response.status_code == 200, response.json()
    assert response.json()["rating_text"] == review.rating_text


def test_edit_review_rating_text_out_of_bounds_returns_400(users, games, create_review, edit_review_request):
    """Alice tenta editar sua review com um texto maior que o permitido"""

    user = users["Alice"]
    game_id = games["roblox"][0]

    review = create_review(user, game_id, True)
    review.rating_text = "Alice" * 100

    response = edit_review_request(user, review)
    assert response.status_code == 400, response.json()
    assert response.json() == RATING_TEXT_TOO_BIG_MSG

