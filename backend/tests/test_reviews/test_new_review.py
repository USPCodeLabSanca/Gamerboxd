import pytest
import requests

from ..utils import Clearence, BASE_URL_REVIEWS, NOT_LOGGED_IN_MSG, GAME_NOT_FOUND_MSG
from .utils import (
    REVIEW_ALREADY_EXISTS_MSG, 
    RATING_TEXT_TOO_BIG_MSG, 
    RATING_TEXT_BLANK_MSG, 
    RATING_NUM_INVALID_MSG, 
    REVIEW_PRIVACY_INVALID_MSG,
    TIME_PLAYED_INVALID_MSG
    )

SUCCESS_CREATING_MSG = {"message":"Review criada com sucesso!", "review_id": "abc"}

def base_review(**overrides):
    """Payload padrão de uma review válida. O campo 'game' é preenchido em runtime
    com um id real vindo da fixture `games`, a menos que já tenha sido sobrescrito."""
 
    review = {
        "game_id": -1,
        "rating_num": 4.5,
        "rating_text": "Muito bom, recomendo!",
        "time_played": 10,
        "liked": True,
        "completed": True,
        "privacy": Clearence.ANY
    }
    review.update(overrides)
    return review
 
 
new_reviews = [
    # Testes funcionais
    (base_review(), 200, SUCCESS_CREATING_MSG),
    (base_review(rating_text=None), 200, SUCCESS_CREATING_MSG),
    ({k: v for k, v in base_review().items() if k != "rating_text"}, 200, SUCCESS_CREATING_MSG),
    (base_review(time_played=None), 200, SUCCESS_CREATING_MSG),
    ({k: v for k, v in base_review().items() if k != "time_played"}, 200, SUCCESS_CREATING_MSG),
    (base_review(rating_num=2), 200, SUCCESS_CREATING_MSG),
    (base_review(liked=0, completed=1), 200, SUCCESS_CREATING_MSG),
    
    # Testes de quebra de regras de negócio pelo usuário
    (base_review(), 409, REVIEW_ALREADY_EXISTS_MSG),
    (base_review(rating_text="a" * 301), 400, RATING_TEXT_TOO_BIG_MSG),
    (base_review(rating_text="       "), 400, RATING_TEXT_BLANK_MSG),
    (base_review(time_played=-10000000), 400, TIME_PLAYED_INVALID_MSG),

    # Testes de quebra de regras de negócio pelo cliente
    (base_review(game_id=0), 404, GAME_NOT_FOUND_MSG),
    (base_review(rating_num=-1.0), 422, RATING_NUM_INVALID_MSG),
    (base_review(rating_num=6.0), 422, RATING_NUM_INVALID_MSG),
    (base_review(rating_num=1.3), 422, RATING_NUM_INVALID_MSG),
    (base_review(privacy=10), 422, REVIEW_PRIVACY_INVALID_MSG),
 
    # Testes de schema inválido/mal formatado - campos obrigatórios ausentes
    ({k: v for k, v in base_review().items() if k != "game_id"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "rating_num"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "privacy"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "liked"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "completed"}, 422, None),
 
    # Testes de schema inválido/mal formatado - tipos errados
    (base_review(game_id="abc"), 422, None),
    (base_review(game_id=None), 422, None),
    (base_review(rating_num="alta"), 422, None),
    (base_review(rating_num=None), 422, None),
    (base_review(rating_text=12345), 422, None),
    (base_review(rating_text=[]), 422, None),
    (base_review(liked="talvez"), 422, None),
    (base_review(liked=None), 422, None),
    (base_review(completed="quase"), 422, None),
    (base_review(completed={}), 422, None),
    (base_review(privacy="segredo"), 422, None),
    (base_review(privacy={}), 422, None),
    (base_review(time_played="muito"), 422, None),
    (base_review(time_played=[]), 422, None),
 
    # Vazio
    ({}, 422, None),
]
 
@pytest.mark.parametrize("review, expected_status, expected_body", new_reviews)
def test_new_review(users, games, review, expected_status, expected_body):
    """Testa a criação de reviews: sucesso, review duplicada, texto muito longo e schema inválido"""
 
    user = users("Alice")
    cookies = user.cookies
    game_id = games["mario"][0]
 
    if "game_id" in review.keys() and review["game_id"] == -1:
        review["game_id"] = game_id
 
    # Força a duplicidade para testes de conflito
    if expected_status == 409:
        setup_response = requests.post(url=BASE_URL_REVIEWS, json=base_review(game_id=game_id), cookies=cookies)
        assert setup_response.status_code == 200, setup_response.json()
        setup_review_id = setup_response.json()["review_id"]
 
    response = requests.post(url=BASE_URL_REVIEWS, json=review, cookies=cookies)
    assert response.status_code == expected_status, response.json()
 
    if expected_body is not None:
        assert response.json().keys() == expected_body.keys()
        assert response.json()["message"] == expected_body["message"]

        review_id = response.json()["review_id"] if response.status_code == 200 else None

    # Limpa a review do DB caso a sua inserção tenha dado certo
    if response.status_code == 200:
        response_delete = requests.delete(url=BASE_URL_REVIEWS + f"/{review_id}", cookies=cookies)
        assert response_delete.status_code == 200, response_delete.json()

    # Se era teste de conflito, remove o duplicado do DB
    if expected_status == 409:
        response_delete_setup = requests.delete(url=BASE_URL_REVIEWS + f"/{setup_review_id}", cookies=cookies)
        assert response_delete_setup.status_code == 200, response_delete_setup.json()


def test_creating_review_while_not_logged_in_returns_401():
    """Um usuário tenta escrever uma review sem enviar os seus cookies de autenticação"""

    response = requests.post(BASE_URL_REVIEWS, json={"rating_num": 5.0})
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG