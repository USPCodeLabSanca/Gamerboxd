from .utils import *


def base_review(**overrides):
    """Payload padrão de uma review válida. O campo 'game' é preenchido em runtime
    com um id real vindo da fixture `games`, a menos que já tenha sido sobrescrito."""
 
    review = {
        "game_id": -1,
        "rating_num": 4.5,
        "rating_text": "Muito bom, recomendo!",
        "liked": True,
        "privacy": Clearence.ANY,
        "time_played": 15,
        "completed": True,
    }
    review.update(overrides)
    return review
 
 
new_reviews = [
    # Testes funcionais
    (base_review(), 200, SUCCESS_CREATING_MSG),
    (base_review(rating_text=None), 200, SUCCESS_CREATING_MSG),
    ({k: v for k, v in base_review().items() if k != "rating_text"}, 200, SUCCESS_CREATING_MSG),
    (base_review(liked=False, privacy=10, completed=False, time_played=0.0, rating_num=0.0), 200, SUCCESS_CREATING_MSG),
    (base_review(rating_text="a" * 280), 200, SUCCESS_CREATING_MSG),
 
    # BaseReview duplicada (mesmo usuário, mesmo jogo)
    (base_review(), 409, REVIEW_ALREADY_EXISTS),
 
    # Texto da review excede o limite de caracteres
    (base_review(rating_text="a" * 301), 400, RATING_TEXT_TOO_BIG_MSG),
 
    # Testes de schema inválido/mal formatado - campos obrigatórios ausentes
    ({k: v for k, v in base_review().items() if k != "game_id"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "rating_num"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "liked"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "privacy"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "completed"}, 422, None),
 
    # Testes de schema inválido/mal formatado - tipos errados
    (base_review(game_id="abc"), 422, None),
    (base_review(game_id=None), 422, None),
    (base_review(rating_num="alta"), 422, None),
    (base_review(rating_text=12345), 422, None),
    (base_review(liked="talvez"), 422, None),
    (base_review(privacy=[]), 422, None),
    (base_review(time_played="muito"), 422, None),
    (base_review(completed={}), 422, None),
 
    # Vazio
    ({}, 422, None),
]
 
 
@pytest.mark.parametrize("review_in,expected_status,expected_body", new_reviews)
def test_new_review(users, games, review_in, expected_status, expected_body):
    """Testa a criação de reviews: sucesso, review duplicada, texto muito longo e schema inválido"""
 
    user = users["Alice"]
    cookies = user.cookies
    game_id = games["mario"][0]
 
    if "game_id" in review_in.keys() and review_in["game_id"] == -1:
        review_in["game_id"] = game_id
 
    # Força a duplicidade para testes de conflito
    if expected_status == 409:
        setup_response = requests.post(url=BASE_URL_REVIEWS, json=base_review(game_id=game_id), cookies=cookies)
        assert setup_response.status_code == 200, setup_response.json()
        setup_review_id = setup_response.json()["review_id"]
 
    response = requests.post(url=BASE_URL_REVIEWS, json=review_in, cookies=cookies)
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
