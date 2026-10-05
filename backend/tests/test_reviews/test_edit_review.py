from .utils import *

# users é um fixture definido em tests/conftest.py
# games é um fixture definido em tests/conftest.py
# create_review é um fixture definido em tests/test_reviews/conftest.py
# edit_review é um fixture definido em tests/test_reviews/conftest.py

def test_edit_review_valid_fields_returns_200(users, games, create_review, edit_review):
    """Alice cria uma review e edita a nota, se curtiu e o texto"""

    user = users["Alice"]
    game_id = games["mario"][0][0]

    review = create_review(user, game_id)
    review_edit = review.copy()

    review_edit["rating_num"] = 10.0
    review_edit["liked"] = False
    review_edit["rating_text"] = "Novo texto"

    response = edit_review(user, game_id, review_edit, review)
    assert response.status_code == 200, response.json()

    updated_review = response.json()
    assert updated_review["rating_num"] == 10.0
    assert updated_review["liked"] is False
    assert updated_review["rating_text"] == review_edit["rating_text"]


def test_edit_review_change_game_returns_400(users, games, create_review, edit_review):
    """Alice tenta trocar o jogo de uma review já existente, o que não é permitido"""

    user = users["Alice"]
    game_id = games["mario"][0][0]
    other_game_id = games["GTA"][0][0]

    review = create_review(user, game_id)
    review_edit = review.copy()
    review_edit["game"] = other_game_id

    response = edit_review(user, game_id, review_edit)
    assert response.status_code == 400, response.json()
    assert response.json() == {"message": "O jogo não pode ser alterado!"}


def test_edit_review_not_found_returns_404(users, games, edit_review):
    """Alice tenta editar uma review de um jogo que ele nunca avaliou"""

    user = users["Alice"]
    game_id = games["roblox"][0][0]

    review = {
        "game": game_id,
        "rating_num": 5.0,
        "rating_text": "Nunca cheguei a jogar de verdade",
        "liked": False,
        "is_private": False,
        "time_played": 1.0,
        "completed": False,
    }

    response = edit_review(user, game_id, review)
    assert response.status_code == 404, response.json()
    assert response.json() == {"message": "Review antiga não encontrada!"}


def test_edit_review_rating_text_return_200(users, games, create_review, edit_review):
    """Alice edita apenas o texto da sua review"""

    user = users["Alice"]
    game_id = games["GTA"][0][0]

    review = create_review(user, game_id)
    review_edit = review.copy()
    review_edit["rating_text"] = "Novo texto"

    response = edit_review(user, game_id, review_edit, review)
    assert response.status_code == 200, response.json()
    assert response.json()["rating_text"] == review_edit["rating_text"]


def test_edit_review_rating_text_out_of_bounds_returns_400(users, games, create_review, edit_review):
    """Alice tenta editar sua review com um texto maior que o permitido"""

    user = users["Alice"]
    game_id = games["roblox"][0][0]

    review = create_review(user, game_id)
    review_edit = review.copy()
    review_edit["rating_text"] = "Alice" * 61

    response = edit_review(user, game_id, review_edit)
    assert response.status_code == 400, response.json()
    assert response.json() == {"message": "O texto da review não pode exceder 300 caractéres"}
