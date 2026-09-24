from . import *
from .utils import create_review, delete_review


def edit_review(user: dict, old_game_id: int, review_in: dict):
    return requests.put(f"{BASE_URL}/{old_game_id}", cookies=user["cookies"], json=review_in)


# ========= Testes ===========

def test_edit_review_valid_fields(users, games):
    """Alice cria uma review e edita a nota, se curtiu e o texto"""

    user = users["Alice"]
    game_id = games["mario"][0][0]

    review = create_review(user, game_id)

    review["rating_num"] = 10.0
    review["liked"] = False
    review["rating_text"] = "Novo texto"

    response = edit_review(user, game_id, review)
    assert response.status_code == 200, f"{response.json()}"

    updated_review = response.json()
    assert updated_review["rating_num"] == 10.0
    assert updated_review["liked"] is False
    assert updated_review["rating_text"] == review["rating_text"]

    delete_review(user, game_id)


def test_edit_review_change_game(users, games):
    """Bernardo tenta trocar o jogo de uma review já existente, o que não é permitido"""

    user = users["Bernardo"]
    game_id = games["mario"][0][0]
    other_game_id = games["GTA"][0][0]

    review = create_review(user, game_id)
    review["game"] = other_game_id

    response = edit_review(user, game_id, review)
    assert response.status_code == 400
    assert response.json() == {"message": "O jogo não pode ser alterado!"}

    delete_review(user, game_id)


def test_edit_review_not_found(users, games):
    """Caua tenta editar uma review de um jogo que ele nunca avaliou"""

    user = users["Caua"]
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
    assert response.status_code == 404
    assert response.json() == {"message": "Review antiga não encontrada!"}


def test_edit_review_rating_text(users, games):
    """Daniela edita apenas o texto da sua review"""

    user = users["Daniela"]
    game_id = games["GTA"][0][0]

    review = create_review(user, game_id)
    review["rating_text"] = "Novo texto"

    response = edit_review(user, game_id, review)
    assert response.status_code == 200
    assert response.json()["rating_text"] == review["rating_text"]

    delete_review(user, game_id)


def test_edit_review_rating_text_out_of_bounds(users, games):
    """Eduarda tenta editar sua review com um texto maior que o permitido"""

    user = users["Eduarda"]
    game_id = games["roblox"][0][0]

    review = create_review(user, game_id)
    review["rating_text"] = "Eduarda" * 50

    response = edit_review(user, game_id, review)
    assert response.status_code == 400
    assert response.json() == {"message": "O texto da review não pode exceder 300 caractéres"}

    delete_review(user, game_id)